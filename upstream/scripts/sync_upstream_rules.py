from pathlib import Path
from urllib.request import Request, build_opener, HTTPSHandler
import ssl, json, subprocess, time, random
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import CLASH_RULES, UA_CLASH

report = {'meta': {'note': 'failed + kept_last_good=true means latest fetch failed but existing verified file was preserved', 'schedule_hint': 'sync-upstream-rules.yml cron 23 3 * * * (UTC, daily)'}}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = build_opener(HTTPSHandler(context=ctx))

def fetch_text(url, ua='minis'):
    req = Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with opener.open(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def fetch_with_curl(url, ua='mihomo/1.18.10', tries=3, pause=8):
    errors = []
    for idx in range(tries):
        # 增加随机延迟，避免被识别为批量爬虫
        if idx > 0:
            time.sleep(pause + random.uniform(0, 5))
        else:
            time.sleep(random.uniform(2, 5))
        
        r = subprocess.run([
            'curl','-L','-k',
            '--retry','2','--retry-all-errors','--retry-delay','3',
            '--connect-timeout','30','--max-time','120',
            '-A',ua,
            '-H','Accept: application/yaml,text/yaml,*/*',
            '-H','Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
            '-H','Accept-Encoding: gzip, deflate, br',
            '-H','Referer: https://kelee.one/',
            '-H','Origin: https://kelee.one',
            '-H','Connection: keep-alive',
            '--compressed',
            '-sS',url
        ], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            text = r.stdout
            if looks_like_payload(text):
                return text
            errors.append(f'try {idx+1}: challenge or invalid payload')
        else:
            errors.append(f'try {idx+1}: {r.stderr.strip() or f"curl exit {r.returncode}"}')
    raise RuntimeError(' | '.join(errors[-3:]) or 'curl failed')

def fetch_plain_with_curl(url, ua='Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', tries=3, pause=6):
    errors = []
    for idx in range(tries):
        # 增加随机延迟，避免被识别为批量爬虫
        if idx > 0:
            time.sleep(pause + random.uniform(0, 4))
        else:
            time.sleep(random.uniform(1, 3))
        
        r = subprocess.run([
            'curl','--http1.1','-L','-k','--compressed',
            '--retry','2','--retry-all-errors','--retry-delay','2',
            '--connect-timeout','25','--max-time','120',
            '-A',ua,
            '-H','Accept: text/plain,*/*',
            '-H','Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            '-H','Accept-Encoding: gzip, deflate, br',
            '-H','Cache-Control: no-cache',
            '-H','Pragma: no-cache',
            '-H','Sec-Fetch-Dest: empty',
            '-H','Sec-Fetch-Mode: cors',
            '-H','Sec-Fetch-Site: cross-site',
            '-sS',url
        ], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        errors.append(f'try {idx+1}: {r.stderr.strip() or f"curl exit {r.returncode}"}')
    raise RuntimeError(' | '.join(errors[-3:]) or 'curl failed')

def looks_like_payload(text):
    head = text[:400].lower()
    if '<!doctype html' in head or '<html' in head or 'just a moment' in head:
        return False
    for line in text.splitlines()[:20]:
        if line.strip() == 'payload:':
            return True
    return False

def save(rel, text):
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def keep_existing_payload(rel):
    p = Path(rel)
    if not p.exists():
        return False
    try:
        return looks_like_payload(p.read_text(encoding="utf-8"))
    except Exception:
        return False

report['core']={'ok':[],'failed':[],'kept':[],'source':{},'status':{}}

# 从 config.py 动态读取所有 Clash 规则（包括 LAN, ESET_China, AI）
verified_core = {}
for name, url in CLASH_RULES.items():
    verified_core[name] = (url, 'urllib', UA_CLASH)
for name, (url, method, ua) in verified_core.items():
    rel = f'upstream/core/{name}.yaml'
    try:
        # 增加随机延迟，避免频繁请求（2-5秒）
        time.sleep(random.uniform(2, 5))
        
        # 尝试 urllib，失败后回退到 curl
        try:
            text = fetch_text(url, ua)
        except Exception as urllib_err:
            print(f'  {name}: urllib failed, trying curl... ({urllib_err})')
            text = fetch_with_curl(url, ua, tries=3, pause=6)
        
        if not looks_like_payload(text):
            raise RuntimeError('invalid payload content')
        save(rel, text)
        report['core']['ok'].append(name)
        report['core']['source'][name] = {'url': url, 'method': 'urllib-or-curl', 'ua': ua}
        report['core']['status'][name] = 'updated-verified'
    except Exception as e:
        kept = keep_existing_payload(rel)
        if kept:
            report['core']['kept'].append(name)
            report['core']['source'][name] = {'url': url, 'method': 'last-known-good', 'ua': ua, 'note': 'latest fetch failed; kept existing verified file'}
            report['core']['status'][name] = 'kept-last-known-good'
        else:
            report['core']['status'][name] = 'failed-verified'
        report['core']['failed'].append({'name':name,'url':url,'method':method,'error':str(e),'kept_last_good':kept})

# Loon remote rule mirrors: keep exact upstream content where possible, with last-known-good fallback
report['loon_remote']={'ok':[],'failed':[],'kept':[],'source':{},'status':{}}
loon_remote_sources = {
    # 基础规则（2 项）
    'LAN_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/LAN_SPLITTER.lsr',
    'REGION_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/REGION_SPLITTER.lsr',
    # AI 服务（4 项）
    'AI': 'https://kelee.one/Tool/Loon/Lsr/AI.lsr',
    'OpenAI': 'https://rule.kelee.one/Loon/OpenAI.lsr',
    'Claude': 'https://rule.kelee.one/Loon/Claude.lsr',
    'Gemini': 'https://rule.kelee.one/Loon/Gemini.lsr',
    'Anthropic': 'https://rule.kelee.one/Loon/Anthropic.lsr',
    'Copilot': 'https://rule.kelee.one/Loon/Copilot.lsr',
    # 流媒体（6 项）
    'Netflix': 'https://rule.kelee.one/Loon/Netflix.lsr',
    'Disney': 'https://rule.kelee.one/Loon/Disney.lsr',
    'YouTube': 'https://rule.kelee.one/Loon/YouTube.lsr',
    'Spotify': 'https://rule.kelee.one/Loon/Spotify.lsr',
    'HBO': 'https://rule.kelee.one/Loon/HBO.lsr',
    'PrimeVideo': 'https://rule.kelee.one/Loon/PrimeVideo.lsr',
    'Bahamut': 'https://rule.kelee.one/Loon/Bahamut.lsr',
    'Emby': 'https://rule.kelee.one/Loon/Emby.lsr',
    # 社交（4 项）
    'Telegram': 'https://rule.kelee.one/Loon/Telegram.lsr',
    'Twitter': 'https://rule.kelee.one/Loon/Twitter.lsr',
    'Facebook': 'https://rule.kelee.one/Loon/Facebook.lsr',
    'Instagram': 'https://rule.kelee.one/Loon/Instagram.lsr',
    # 平台（6 项）
    'Apple': 'https://rule.kelee.one/Loon/Apple.lsr',
    'AppleAccount': 'https://kelee.one/Tool/Loon/Lsr/AppleAccount.lsr',
    'AppStore': 'https://kelee.one/Tool/Loon/Lsr/AppStore.lsr',
    'AppleTV': 'https://rule.kelee.one/Loon/AppleTV.lsr',
    'Google': 'https://rule.kelee.one/Loon/Google.lsr',
    'GoogleFCM': 'https://rule.kelee.one/Loon/GoogleFCM.lsr',
    'Microsoft': 'https://rule.kelee.one/Loon/Microsoft.lsr',
    'GitHub': 'https://rule.kelee.one/Loon/GitHub.lsr',
    # 其他（6 项）
    'TikTok': 'https://kelee.one/Tool/Loon/Lsr/TikTok.lsr',
    'Game': 'https://rule.kelee.one/Loon/Game.lsr',
    'Speedtest': 'https://rule.kelee.one/Loon/Speedtest.lsr',
    'Steam': 'https://rule.kelee.one/Loon/Steam.lsr',
    'ReelShort': 'https://kelee.one/Tool/Loon/Lsr/ReelShort.lsr',
    'Proxy': 'https://kelee.one/Tool/Loon/Lsr/Proxy.lsr',
    'Direct': 'https://kelee.one/Tool/Loon/Lsr/Direct.lsr',
}

def looks_like_loon_rules(text):
    head = text[:500].lower()
    if '<!doctype html' in head or '<html' in head or 'just a moment' in head or 'cf-chl' in head:
        return False
    cnt = 0
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith('#') or s.startswith('//') or s.startswith(';'):
            continue
        if ',' in s:
            cnt += 1
    return cnt > 0

def keep_existing_loon(rel):
    p = Path(rel)
    if not p.exists():
        return False
    try:
        return looks_like_loon_rules(p.read_text(encoding='utf-8'))
    except Exception:
        return False

for name, url in loon_remote_sources.items():
    rel = f'upstream/loon/{name}.lsr'
    try:
        # 增加随机延迟，模拟真实客户端行为（2-5秒）
        time.sleep(random.uniform(2, 5))
        text = fetch_plain_with_curl(url, 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', tries=3, pause=6)
        if not looks_like_loon_rules(text):
            raise RuntimeError('invalid loon rule content')
        save(rel, text)
        report['loon_remote']['ok'].append(name)
        report['loon_remote']['source'][name] = {'url': url, 'method': 'validated-curl', 'ua': 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 'tries': 3}
        report['loon_remote']['status'][name] = 'updated-verified'
    except Exception as e:
        kept = keep_existing_loon(rel)
        if kept:
            report['loon_remote']['kept'].append(name)
            report['loon_remote']['source'][name] = {'url': url, 'method': 'last-known-good', 'ua': 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 'tries': 3, 'note': 'latest fetch failed; kept existing verified file'}
            report['loon_remote']['status'][name] = 'kept-last-known-good'
        else:
            report['loon_remote']['status'][name] = 'failed-verified'
        report['loon_remote']['failed'].append({'name': name, 'url': url, 'error': str(e), 'kept_last_good': kept})

save('upstream/_sync_report.json', json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'core_ok':len(report['core']['ok']),'core_failed':len(report['core']['failed']),'loon_ok':len(report['loon_remote']['ok']),'loon_failed':len(report['loon_remote']['failed'])}, ensure_ascii=False))
