from pathlib import Path
from urllib.request import Request, urlopen

TARGETS = {
    "upstream/ShuntRules/LAN.yaml": "https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml",
    "upstream/ShuntRules/Direct.yaml": "https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Direct.yaml",
    "upstream/ShuntRules/AI.yaml": "https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/AI.yaml",
    "upstream/ShuntRules/Netflix.yaml": "https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/Netflix.yaml",
    "upstream/ShuntRules/ESET_China.yaml": "https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml",
}

for rel, url in TARGETS.items():
    req = Request(url, headers={"User-Agent": "minis"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    p = Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")
    print(f"synced {rel}")
