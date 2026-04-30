from pathlib import Path
from urllib.request import Request, build_opener, HTTPSHandler
import ssl, json, subprocess, time, random

report = {'meta': {'note': 'failed + kept_last_good=true means latest fetch failed but existing verified file was preserved', 'schedule_hint': 'sync-upstream-rules.yml cron 23 3 * * * (UTC, daily)'}}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = build_opener(HTTPSHandler(context=ctx))

def fetch_text(url, ua='minis'):
    req = Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with opener.open(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def fetch_with_curl(url, ua='mihomo/1.18.10', tries=1, pause=8):
    errors = []
    for idx in range(tries):
        # 增加随机延迟，避免被识别为批量爬虫（首次请求也延迟）
        time.sleep(random.uniform(5, 10))
        
        r = subprocess.run([
            'curl','-L','-k',
            '--retry','1','--retry-all-errors',
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
            errors.append('challenge or invalid payload content')
        else:
            errors.append(r.stderr.strip() or f'curl exit {r.returncode}')
    raise RuntimeError(' | '.join(errors[-3:]) or 'curl failed')

def fetch_plain_with_curl(url, ua='Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', tries=1, pause=8):
    errors = []
    for idx in range(tries):
        # 增加随机延迟，避免被识别为批量爬虫
        if idx > 0:
            time.sleep(pause + random.uniform(0, 3))
        
        r = subprocess.run([
            'curl','--http1.1','-L','-k','--compressed',
            '--retry','1','--retry-all-errors',
            '--connect-timeout','20','--max-time','120',
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
        errors.append(r.stderr.strip() or f'curl exit {r.returncode}')
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
static_core = {
    'LAN': ('https://kelee.one/Tool/Clash/Rule/LAN_SPLITTER.yaml', 'curl', 'mihomo/1.18.10'),
    'ESET_China': ('https://kelee.one/Tool/Clash/Rule/ESET_China.yaml', 'curl', 'mihomo/1.18.10'),
}
for name, (url, method, ua) in static_core.items():
    try:
        if method == 'curl':
            text = fetch_with_curl(url, ua, 2)
        else:
            text = fetch_text(url, ua)
        if not looks_like_payload(text):
            raise RuntimeError('invalid payload content')
        save(f'upstream/core/{name}.yaml', text)
        report['core']['ok'].append(name)
        report['core']['source'][name] = {'url': url, 'method': method, 'ua': ua}
        report['core']['status'][name] = 'updated-static'
    except Exception as e:
        report['core']['status'][name] = 'failed-static'
        report['core']['failed'].append({'name':name,'url':url,'method':method,'error':str(e)})

verified_core = {
    # 文件内明确给出的规则（8 项）
    'LAN': ('https://kelee.one/Tool/Clash/Rule/LAN_SPLITTER.yaml', 'urllib', 'clash.meta'),
    'Direct': ('https://kelee.one/Tool/Clash/Rule/Direct.yaml', 'urllib', 'clash.meta'),
    'Proxy': ('https://kelee.one/Tool/Clash/Rule/Proxy.yaml', 'urllib', 'clash.meta'),
    'AI': ('https://kelee.one/Tool/Clash/Rule/AI.yaml', 'urllib', 'clash.meta'),
    'TikTok': ('https://kelee.one/Tool/Clash/Rule/TikTok.yaml', 'urllib', 'clash.meta'),
    'Game': ('https://kelee.one/Tool/Clash/Rule/Game.yaml', 'urllib', 'clash.meta'),
    'Netflix': ('https://rule.kelee.one/Clash/Netflix.yaml', 'urllib', 'clash.meta'),
    'ESET_China': ('https://kelee.one/Tool/Clash/Rule/ESET_China.yaml', 'urllib', 'clash.meta'),
    # 文件里没有的，参考 luestr/ShuntRules（3 项）
    'Telegram': ('https://rule.kelee.one/Clash/Telegram.yaml', 'urllib', 'clash.meta'),
    'Google': ('https://rule.kelee.one/Clash/Google.yaml', 'urllib', 'clash.meta'),
    'Apple': ('https://rule.kelee.one/Clash/Apple.yaml', 'urllib', 'clash.meta'),
}
for name, (url, method, ua) in verified_core.items():
    rel = f'upstream/core/{name}.yaml'
    try:
        # 增加随机延迟，避免频繁请求（2-5秒）
        time.sleep(random.uniform(2, 5))
        text = fetch_text(url, ua)
        if not looks_like_payload(text):
            raise RuntimeError('invalid payload content')
        save(rel, text)
        report['core']['ok'].append(name)
        report['core']['source'][name] = {'url': url, 'method': 'urllib', 'ua': ua}
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

# AI 聚合：改为 blackmatrix7 8 项聚合，并在失败时保留 last-known-good
ai_sources = [
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BardAI/BardAI.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Anthropic/Anthropic.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Jetbrains/Jetbrains.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/aiXcoder/aiXcoder.yaml',
]
try:
    texts=[]
    for url in ai_sources:
        text = fetch_text(url, 'minis')
        if not looks_like_payload(text):
            raise RuntimeError(f'AI source invalid payload: {url}')
        texts.append(text)
    seen=set(); out=['payload:']
    for text in texts:
        for raw in text.splitlines():
            s=raw.strip()
            if not s or s=='payload:' or s.startswith('#'): continue
            item=s[2:].strip() if s.startswith('- ') else s
            item=item.strip().strip('"').strip("'")
            if item.startswith('IP-CIDR,') and not item.endswith(',no-resolve'):
                item = item + ',no-resolve'
            if item.startswith('IP-ASN,') and not item.endswith(',no-resolve'):
                item = item + ',no-resolve'
            if item and item not in seen:
                seen.add(item); out.append(f'  - "{item}"')
    save('upstream/core/AI.yaml', '\n'.join(out).rstrip()+'\n')
    report['core']['ok'].append('AI')
    report['core']['source']['AI']={'url':ai_sources,'method':'bm7-raw-aggregate','ua':'minis'}
    report['core']['status']['AI'] = 'updated-bm7-aggregate'
except Exception as e:
    kept = keep_existing_payload('upstream/core/AI.yaml')
    if kept:
        report['core']['kept'].append('AI')
        report['core']['source']['AI']={'url':ai_sources,'method':'last-known-good-bm7-aggregate','ua':'minis','note':'latest fetch failed; kept existing verified file'}
        report['core']['status']['AI'] = 'kept-last-known-good-bm7-aggregate'
    else:
        report['core']['status']['AI'] = 'failed-bm7-aggregate'
    report['core']['failed'].append({'name':'AI','error':str(e),'kept_last_good':kept})

# Loon remote rule mirrors: keep exact upstream content where possible, with last-known-good fallback
report['loon_remote']={'ok':[],'failed':[],'kept':[],'source':{},'status':{}}
loon_remote_sources = {
    # 已有规则（14 项）
    'Telegram': 'https://rule.kelee.one/Loon/Telegram.lsr',
    'TikTok': 'https://kelee.one/Tool/Loon/Lsr/TikTok.lsr',
    'AI': 'https://kelee.one/Tool/Loon/Lsr/AI.lsr',
    'AppleAccount': 'https://kelee.one/Tool/Loon/Lsr/AppleAccount.lsr',
    'AppStore': 'https://kelee.one/Tool/Loon/Lsr/AppStore.lsr',
    'GitHub': 'https://rule.kelee.one/Loon/GitHub.lsr',
    'Netflix': 'https://rule.kelee.one/Loon/Netflix.lsr',
    'YouTube': 'https://rule.kelee.one/Loon/YouTube.lsr',
    'Disney': 'https://rule.kelee.one/Loon/Disney.lsr',
    'Twitter': 'https://rule.kelee.one/Loon/Twitter.lsr',
    'Facebook': 'https://rule.kelee.one/Loon/Facebook.lsr',
    'Instagram': 'https://rule.kelee.one/Loon/Instagram.lsr',
    'Spotify': 'https://rule.kelee.one/Loon/Spotify.lsr',
    'Google': 'https://rule.kelee.one/Loon/Google.lsr',
    # 新增规则（18 项）
    'Anthropic': 'https://rule.kelee.one/Loon/Anthropic.lsr',
    'Apple': 'https://rule.kelee.one/Loon/Apple.lsr',
    'AppleTV': 'https://rule.kelee.one/Loon/AppleTV.lsr',
    'Bahamut': 'https://rule.kelee.one/Loon/Bahamut.lsr',
    'Claude': 'https://rule.kelee.one/Loon/Claude.lsr',
    'Copilot': 'https://rule.kelee.one/Loon/Copilot.lsr',
    'Emby': 'https://rule.kelee.one/Loon/Emby.lsr',
    'Game': 'https://rule.kelee.one/Loon/Game.lsr',
    'Gemini': 'https://rule.kelee.one/Loon/Gemini.lsr',
    'GoogleFCM': 'https://rule.kelee.one/Loon/GoogleFCM.lsr',
    'HBO': 'https://rule.kelee.one/Loon/HBO.lsr',
    'LAN_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/LAN_SPLITTER.lsr',
    'Microsoft': 'https://rule.kelee.one/Loon/Microsoft.lsr',
    'OpenAI': 'https://rule.kelee.one/Loon/OpenAI.lsr',
    'PrimeVideo': 'https://rule.kelee.one/Loon/PrimeVideo.lsr',
    'REGION_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/REGION_SPLITTER.lsr',
    'Speedtest': 'https://rule.kelee.one/Loon/Speedtest.lsr',
    'Steam': 'https://rule.kelee.one/Loon/Steam.lsr',
    # 用户要求新增（2 项）
    'ReelShort': 'https://kelee.one/Tool/Loon/Lsr/ReelShort.lsr',
    'Filen': 'https://kelee.one/Tool/Loon/Rule/Filen.list',
    # 其他常用服务（8 项）
    'Amazon': 'https://kelee.one/Tool/Loon/Lsr/Amazon.lsr',
    'Reddit': 'https://kelee.one/Tool/Loon/Lsr/Reddit.lsr',
    'Twitch': 'https://kelee.one/Tool/Loon/Lsr/Twitch.lsr',
    'WhatsApp': 'https://kelee.one/Tool/Loon/Lsr/WhatsApp.lsr',
    'Discord': 'https://kelee.one/Tool/Loon/Lsr/Discord.lsr',
    'PayPal': 'https://kelee.one/Tool/Loon/Lsr/PayPal.lsr',
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
        text = fetch_plain_with_curl(url, 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 2, 3)
        if not looks_like_loon_rules(text):
            raise RuntimeError('invalid loon rule content')
        save(rel, text)
        report['loon_remote']['ok'].append(name)
        report['loon_remote']['source'][name] = {'url': url, 'method': 'validated-curl', 'ua': 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 'tries': 4}
        report['loon_remote']['status'][name] = 'updated-verified'
    except Exception as e:
        kept = keep_existing_loon(rel)
        if kept:
            report['loon_remote']['kept'].append(name)
            report['loon_remote']['source'][name] = {'url': url, 'method': 'last-known-good', 'ua': 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 'tries': 4, 'note': 'latest fetch failed; kept existing verified file'}
            report['loon_remote']['status'][name] = 'kept-last-known-good'
        else:
            report['loon_remote']['status'][name] = 'failed-verified'
        report['loon_remote']['failed'].append({'name': name, 'url': url, 'error': str(e), 'kept_last_good': kept})

save('upstream/_sync_report.json', json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'core_ok':len(report['core']['ok']),'core_failed':len(report['core']['failed']),'loon_ok':len(report['loon_remote']['ok']),'loon_failed':len(report['loon_remote']['failed'])}, ensure_ascii=False))
