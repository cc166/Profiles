from pathlib import Path
from urllib.request import Request, build_opener, HTTPSHandler
import ssl, json

report = {}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
opener = build_opener(HTTPSHandler(context=ctx))

def fetch_text(url, ua='minis'):
    req = Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    with opener.open(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def save(rel, text):
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

# core：已确认部分直接切 iKeLee，未确认部分暂保留过渡源
core_sources = {
    'LAN': ('https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml', 'minis'),
    'Direct': ('https://rule.kelee.one/Clash/Direct.yaml', 'clash.meta'),
    'AI': ('https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/AI.yaml', 'minis'),
    'Game': ('https://rule.kelee.one/Clash/Game.yaml', 'clash.meta'),
    'Netflix': ('https://rule.kelee.one/Clash/Netflix.yaml', 'clash.meta'),
    'ESET_China': ('https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml', 'minis'),
}
report['core']={'ok':[],'failed':[],'source':{}}
for name, (url, ua) in core_sources.items():
    try:
        save(f'upstream/core/{name}.yaml', fetch_text(url, ua))
        report['core']['ok'].append(name)
        report['core']['source'][name] = url
    except Exception as e:
        report['core']['failed'].append({'name':name,'url':url,'error':str(e)})

# 主源：blackmatrix7
bm7_names = ["Apple","YouTube","GitHub","Google","Microsoft","Telegram","Twitter","Discord","Steam","Emby","PayPal","Speedtest","Scholar"]
report['blackmatrix7']={'ok':[],'failed':[]}
for name in bm7_names:
    for url, rel in [
        (f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml", f"upstream/blackmatrix7/clash/{name}.yaml"),
        (f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/{name}/{name}.list", f"upstream/blackmatrix7/loon/{name}.list"),
    ]:
        try:
            save(rel, fetch_text(url)); report['blackmatrix7']['ok'].append(rel)
        except Exception as e:
            report['blackmatrix7']['failed'].append({'path':rel,'url':url,'error':str(e)})

# 补源：yuumimi 最小生成版
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
