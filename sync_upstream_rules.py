from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

FILES = [
    "LAN", "Direct", "Proxy", "AI", "Game", "Netflix", "YouTube",
    "Apple", "Microsoft", "Google", "GitHub", "Telegram", "Twitter",
    "Discord", "Steam", "Emby", "PayPal", "Speedtest", "Scholar",
    "ProxyMedia", "ESET_China",
]

report = {"ok": [], "failed": []}
for name in FILES:
    url = f"https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/{name}.yaml"
    try:
        req = Request(url, headers={"User-Agent": "minis"})
        with urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        p = Path(f"upstream/ShuntRules/{name}.yaml")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data, encoding="utf-8")
        report["ok"].append(name)
        print(f"synced {name}.yaml")
    except Exception as e:
        report["failed"].append({"name": name, "error": str(e)})
        print(f"failed {name}.yaml: {e}")

Path("upstream/ShuntRules/_sync_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps({"ok_count": len(report["ok"]), "failed_count": len(report["failed"])}, ensure_ascii=False))
