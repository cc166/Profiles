from pathlib import Path
from urllib.request import Request, urlopen

FILES = [
    "LAN",
    "Direct",
    "Proxy",
    "AI",
    "Game",
    "Netflix",
    "YouTube",
    "Apple",
    "Microsoft",
    "Google",
    "GitHub",
    "Telegram",
    "Twitter",
    "Discord",
    "Steam",
    "Emby",
    "PayPal",
    "Speedtest",
    "Scholar",
    "ProxyMedia",
    "ESET_China",
]

for name in FILES:
    url = f"https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/{name}.yaml"
    req = Request(url, headers={"User-Agent": "minis"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    p = Path(f"upstream/ShuntRules/{name}.yaml")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")
    print(f"synced {name}.yaml")
