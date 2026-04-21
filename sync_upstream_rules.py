from pathlib import Path
from urllib.request import Request, urlopen
import json

report = {}

def fetch_text(url):
    req = Request(url, headers={"User-Agent": "minis"})
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def save(rel, text):
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

# 兼容保留：ShuntRules
shunt = [
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml", "upstream/ShuntRules/LAN.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Direct.yaml", "upstream/ShuntRules/Direct.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Proxy.yaml", "upstream/ShuntRules/Proxy.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/AI.yaml", "upstream/ShuntRules/AI.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Game.yaml", "upstream/ShuntRules/Game.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Netflix.yaml", "upstream/ShuntRules/Netflix.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml", "upstream/ShuntRules/ESET_China.yaml"),
]

# 主源：blackmatrix7
bm7_names = ["Apple","YouTube","GitHub","Google","Microsoft","Telegram","Twitter","Discord","Steam","Emby","PayPal","Speedtest","Scholar"]
bm7=[]
for name in bm7_names:
    bm7.append((f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml", f"upstream/blackmatrix7/clash/{name}.yaml"))
    bm7.append((f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/{name}/{name}.list", f"upstream/blackmatrix7/loon/{name}.list"))

# 补源：yuumimi（最小可用生成版）
# 基于 domain-list-community 直接生成常用 domain 规则
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

report['ShuntRules']={'ok':[],'failed':[]}
for url, rel in shunt:
    try:
        save(rel, fetch_text(url)); report['ShuntRules']['ok'].append(rel)
    except Exception as e:
        report['ShuntRules']['failed'].append({'path':rel,'url':url,'error':str(e)})

report['blackmatrix7']={'ok':[],'failed':[]}
for url, rel in bm7:
    try:
        save(rel, fetch_text(url)); report['blackmatrix7']['ok'].append(rel)
    except Exception as e:
        report['blackmatrix7']['failed'].append({'path':rel,'url':url,'error':str(e)})

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
print(json.dumps({'shunt_ok':len(report['ShuntRules']['ok']),'bm7_ok':len(report['blackmatrix7']['ok']),'yuumimi_ok':len(report['yuumimi']['ok']),'yuumimi_failed':len(report['yuumimi']['failed'])}, ensure_ascii=False))
