from pathlib import Path
from urllib.request import Request, urlopen
import json

SOURCES = {
  "ShuntRules": [
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml", "upstream/ShuntRules/LAN.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Direct.yaml", "upstream/ShuntRules/Direct.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Proxy.yaml", "upstream/ShuntRules/Proxy.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/AI.yaml", "upstream/ShuntRules/AI.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Game.yaml", "upstream/ShuntRules/Game.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Netflix.yaml", "upstream/ShuntRules/Netflix.yaml"),
    ("https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml", "upstream/ShuntRules/ESET_China.yaml"),
  ],
  "blackmatrix7": [
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Apple/Apple.yaml", "upstream/blackmatrix7/clash/Apple.yaml"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/YouTube/YouTube.yaml", "upstream/blackmatrix7/clash/YouTube.yaml"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GitHub/GitHub.yaml", "upstream/blackmatrix7/clash/GitHub.yaml"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Google/Google.yaml", "upstream/blackmatrix7/clash/Google.yaml"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Microsoft/Microsoft.yaml", "upstream/blackmatrix7/clash/Microsoft.yaml"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Apple/Apple.list", "upstream/blackmatrix7/loon/Apple.list"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/YouTube/YouTube.list", "upstream/blackmatrix7/loon/YouTube.list"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/GitHub/GitHub.list", "upstream/blackmatrix7/loon/GitHub.list"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Google/Google.list", "upstream/blackmatrix7/loon/Google.list"),
    ("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Microsoft/Microsoft.list", "upstream/blackmatrix7/loon/Microsoft.list"),
  ],
  "yuumimi": [
    ("https://raw.githubusercontent.com/yuumimi/rules/main/clash/rule/Apple.yaml", "upstream/yuumimi/clash/Apple.yaml"),
    ("https://raw.githubusercontent.com/yuumimi/rules/main/clash/rule/YouTube.yaml", "upstream/yuumimi/clash/YouTube.yaml"),
    ("https://raw.githubusercontent.com/yuumimi/rules/main/clash/rule/GitHub.yaml", "upstream/yuumimi/clash/GitHub.yaml"),
    ("https://raw.githubusercontent.com/yuumimi/rules/main/loon/rule/Apple.list", "upstream/yuumimi/loon/Apple.list"),
    ("https://raw.githubusercontent.com/yuumimi/rules/main/loon/rule/YouTube.list", "upstream/yuumimi/loon/YouTube.list"),
    ("https://raw.githubusercontent.com/yuumimi/rules/main/loon/rule/GitHub.list", "upstream/yuumimi/loon/GitHub.list"),
  ],
}

report = {}
for source, items in SOURCES.items():
    ok=[]; failed=[]
    for url, rel in items:
        try:
            req = Request(url, headers={"User-Agent": "minis"})
            with urlopen(req, timeout=60) as resp:
                data = resp.read().decode("utf-8", errors="ignore")
            p = Path(rel)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(data, encoding="utf-8")
            ok.append(rel)
            print(f"synced {rel}")
        except Exception as e:
            failed.append({"path": rel, "url": url, "error": str(e)})
            print(f"failed {rel}: {e}")
    report[source] = {"ok": ok, "failed": failed}

Path("upstream/_sync_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
