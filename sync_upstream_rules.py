from pathlib import Path
from urllib.request import Request, urlopen
import json

report = {}

def fetch(url, rel):
    req = Request(url, headers={"User-Agent": "minis"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")

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
common = ["Apple","YouTube","GitHub","Google","Microsoft","Telegram","Twitter","Discord","Steam","Emby","PayPal","Speedtest","Scholar"]
bm7=[]
for name in common:
    bm7.append((f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/{name}/{name}.yaml", f"upstream/blackmatrix7/clash/{name}.yaml"))
    bm7.append((f"https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/{name}/{name}.list", f"upstream/blackmatrix7/loon/{name}.list"))

report['ShuntRules']={'ok':[],'failed':[]}
for url, rel in shunt:
    try:
        fetch(url, rel); report['ShuntRules']['ok'].append(rel)
    except Exception as e:
        report['ShuntRules']['failed'].append({'path':rel,'url':url,'error':str(e)})

report['blackmatrix7']={'ok':[],'failed':[]}
for url, rel in bm7:
    try:
        fetch(url, rel); report['blackmatrix7']['ok'].append(rel)
    except Exception as e:
        report['blackmatrix7']['failed'].append({'path':rel,'url':url,'error':str(e)})

Path('upstream/_sync_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'shunt_ok':len(report['ShuntRules']['ok']),'bm7_ok':len(report['blackmatrix7']['ok']),'bm7_failed':len(report['blackmatrix7']['failed'])}, ensure_ascii=False))
