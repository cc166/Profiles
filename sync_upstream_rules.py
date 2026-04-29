from pathlib import Path
from urllib.request import Request, build_opener, HTTPSHandler
import ssl, json, subprocess, time, random

report = {'meta': {'note': 'failed + kept_last_good=true means latest fetch failed but existing verified file was preserved', 'schedule_hint': 'sync-upstream-rules.yml cron 23 3 */2 * * (UTC)'}}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = build_opener(HTTPSHandler(context=ctx))

def fetch_text(url, ua='minis'):
    req = Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with opener.open(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def fetch_with_curl(url, ua='clash.meta', tries=1, pause=8):
    errors = []
    for idx in range(tries):
        # 增加随机延迟，避免被识别为批量爬虫
        if idx > 0:
            time.sleep(pause + random.uniform(0, 3))
        
        r = subprocess.run([
            'curl','-L','-k',
            '--retry','2','--retry-all-errors',
            '--connect-timeout','20','--max-time','120',
            '-A',ua,
            '-H','Accept: */*',
            '-H','Accept-Language: en-US,en;q=0.9',
            '-H','Accept-Encoding: gzip, deflate, br',
            '-H','Cache-Control: no-cache',
            '-H','Pragma: no-cache',
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
    'LAN': ('https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml', 'urllib', 'minis'),
    'ESET_China': ('https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml', 'urllib', 'minis'),
}
for name, (url, method, ua) in static_core.items():
    try:
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
    # 已有规则（3 项）
    'Direct': ('https://rule.kelee.one/Clash/Direct.yaml', 'curl', 'clash.meta', 6),
    'Game': ('https://rule.kelee.one/Clash/Game.yaml', 'curl', 'clash.meta', 4),
    'Netflix': ('https://rule.kelee.one/Clash/Netflix.yaml', 'curl', 'clash.meta', 4),
    # 新增规则（3 项）
    'Proxy': ('https://kelee.one/Tool/Clash/Rule/Proxy.yaml', 'curl', 'clash.meta', 4),
    'SpeedtestInternational': ('https://kelee.one/Tool/Clash/Rule/SpeedtestInternational.yaml', 'curl', 'clash.meta', 4),
    'TikTok': ('https://kelee.one/Tool/Clash/Rule/TikTok.yaml', 'curl', 'clash.meta', 4),
}
for name, (url, method, ua, tries) in verified_core.items():
    rel = f'upstream/core/{name}.yaml'
    try:
        # 增加随机延迟，避免批量请求被识别
        time.sleep(random.uniform(1, 3))
        text = fetch_with_curl(url, ua, tries)
        if not looks_like_payload(text):
            raise RuntimeError('challenge or invalid payload content')
        save(rel, text)
        report['core']['ok'].append(name)
        report['core']['source'][name] = {'url': url, 'method': 'validated-curl', 'ua': ua, 'tries': tries}
        report['core']['status'][name] = 'updated-verified'
    except Exception as e:
        kept = keep_existing_payload(rel)
        if kept:
            report['core']['kept'].append(name)
            report['core']['source'][name] = {'url': url, 'method': 'last-known-good', 'ua': ua, 'tries': tries, 'note': 'latest fetch failed; kept existing verified file'}
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

# primary/supplement layers keep existing behavior
bm7_names = ["Apple","YouTube","GitHub","Google","Microsoft","Telegram","Twitter","Discord","Steam","Emby","PayPal","Speedtest","Scholar"]
report['blackmatrix7']={'ok':[],'failed':[]}
for name in bm7_names:
    for url, rel in [
        (f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml", f"upstream/blackmatrix7/clash/{name}.yaml"),
        (f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/{name}/{name}.list", f"upstream/blackmatrix7/loon/{name}.list"),
    ]:
        try:
            text = fetch_text(url)
            save(rel, text); report['blackmatrix7']['ok'].append(rel)
        except Exception as e:
            report['blackmatrix7']['failed'].append({'path':rel,'url':url,'error':str(e)})

yuumimi_sets = ["apple","youtube","github","google","microsoft","telegram","twitter","discord","steam","paypal","speedtest","category-scholar-!cn"]
def gen_from_dlc(name):
    url = f"https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/{name}"
    content = fetch_text(url)
    domains=[]
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or line.startswith('include:') or line.startswith('regexp:') or line.startswith('keyword:'):
            continue
        if line.startswith('full:'):
            domains.append(('full', line[5:].strip()))
        elif line.startswith('domain:'):
            domains.append(('suffix', line[7:].strip()))
        else:
            domains.append(('suffix', line))
    return domains
report['yuumimi']={'ok':[],'failed':[]}
for name in yuumimi_sets:
    try:
        domains = gen_from_dlc(name)
        clash = ['payload:']
        loon = []
        for typ, val in domains:
            if not val:
                continue
            if typ == 'full':
                clash.append(f'  - "{val}"')
                loon.append(f'DOMAIN,{val}')
            else:
                clash.append(f'  - "+.{val}"')
                loon.append(f'DOMAIN-SUFFIX,{val}')
        pretty = name.replace('category-scholar-!cn','Scholar').replace('apple','Apple').replace('youtube','YouTube').replace('github','GitHub').replace('google','Google').replace('microsoft','Microsoft').replace('telegram','Telegram').replace('twitter','Twitter').replace('discord','Discord').replace('steam','Steam').replace('paypal','PayPal').replace('speedtest','Speedtest')
        save(f'upstream/yuumimi/clash/{pretty}.yaml', '\n'.join(clash).rstrip()+'\n')
        save(f'upstream/yuumimi/loon/{pretty}.list', '\n'.join(loon).rstrip()+'\n')
        report['yuumimi']['ok'].append(pretty)
    except Exception as e:
        report['yuumimi']['failed'].append({'name':name,'error':str(e)})


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
    'LAN_SPLITTER': 'https://rule.kelee.one/Loon/LAN_SPLITTER.lsr',
    'Microsoft': 'https://rule.kelee.one/Loon/Microsoft.lsr',
    'OpenAI': 'https://rule.kelee.one/Loon/OpenAI.lsr',
    'PrimeVideo': 'https://rule.kelee.one/Loon/PrimeVideo.lsr',
    'REGION_SPLITTER': 'https://rule.kelee.one/Loon/REGION_SPLITTER.lsr',
    'Speedtest': 'https://rule.kelee.one/Loon/Speedtest.lsr',
    'Steam': 'https://rule.kelee.one/Loon/Steam.lsr',
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
        # 增加随机延迟，避免批量请求被识别
        time.sleep(random.uniform(2, 5))
        text = fetch_plain_with_curl(url, 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0', 4, 6)
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
