from pathlib import Path
from urllib.request import Request, build_opener, HTTPSHandler
import ssl, json, subprocess, time

report = {'meta': {'note': 'failed + kept_last_good=true means latest fetch failed but existing verified file was preserved', 'schedule_hint': 'sync-upstream-rules.yml cron 23 3 * * * (UTC)'}}
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
        r = subprocess.run([
            'curl','-L','-k',
            '--retry','2','--retry-all-errors',
            '--connect-timeout','20','--max-time','120',
            '-A',ua,'-H','Accept: */*','-sS',url
        ], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        errors.append(r.stderr.strip() or f'curl exit {r.returncode}')
        if idx < tries - 1:
            time.sleep(pause)
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
    'Direct': ('https://rule.kelee.one/Clash/Direct.yaml', 'curl', 'clash.meta', 6),
    'Game': ('https://rule.kelee.one/Clash/Game.yaml', 'curl', 'clash.meta', 2),
    'Netflix': ('https://rule.kelee.one/Clash/Netflix.yaml', 'curl', 'clash.meta', 2),
}
for name, (url, method, ua, tries) in verified_core.items():
    rel = f'upstream/core/{name}.yaml'
    try:
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

# AI 聚合：扩为 8 项，并在失败时保留 last-known-good
ai_sources = [
    'https://rule.kelee.one/Clash/OpenAI.yaml',
    'https://rule.kelee.one/Clash/BardAI.yaml',
    'https://rule.kelee.one/Clash/Anthropic.yaml',
    'https://rule.kelee.one/Clash/Claude.yaml',
    'https://rule.kelee.one/Clash/Copilot.yaml',
    'https://rule.kelee.one/Clash/Gemini.yaml',
    'https://rule.kelee.one/Clash/Jetbrains.yaml',
    'https://rule.kelee.one/Clash/aiXcoder.yaml',
]
try:
    texts=[]
    for url in ai_sources:
        text = fetch_with_curl(url, 'clash.meta', 2)
        if not looks_like_payload(text):
            raise RuntimeError(f'AI source challenge or invalid payload: {url}')
        texts.append(text)
    seen=set(); out=['payload:']
    for text in texts:
        for raw in text.splitlines():
            s=raw.strip()
            if not s or s=='payload:' or s.startswith('#'): continue
            item=s[2:].strip() if s.startswith('- ') else s
            item=item.strip().strip('"').strip("'")
            if item and item not in seen:
                seen.add(item); out.append(f'  - "{item}"')
    save('upstream/core/AI.yaml', '\n'.join(out).rstrip()+'\n')
    report['core']['ok'].append('AI')
    report['core']['source']['AI']={'url':ai_sources,'method':'validated-curl-aggregate','ua':'clash.meta','tries':2}
    report['core']['status']['AI'] = 'updated-aggregate'
except Exception as e:
    kept = keep_existing_payload('upstream/core/AI.yaml')
    if kept:
        report['core']['kept'].append('AI')
        report['core']['source']['AI']={'url':ai_sources,'method':'last-known-good-aggregate','ua':'clash.meta','tries':2,'note':'latest fetch failed; kept existing verified file'}
        report['core']['status']['AI'] = 'kept-last-known-good-aggregate'
    else:
        report['core']['status']['AI'] = 'failed-aggregate'
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

save('upstream/_sync_report.json', json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'core_ok':len(report['core']['ok']),'core_failed':len(report['core']['failed'])}, ensure_ascii=False))
