# Profiles 规则列表

个人 Loon 和 Clash 配置规则。

## 📊 规则列表

### Loon 规则（32 项）

| 规则名称 | 用途 | Raw 链接 |
|---------|------|---------|
| AI | AI 服务聚合 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/AI.lsr) |
| Anthropic | Anthropic/Claude | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Anthropic.lsr) |
| Apple | Apple 服务 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Apple.lsr) |
| AppleAccount | Apple 账户 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/AppleAccount.lsr) |
| AppStore | App Store | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/AppStore.lsr) |
| AppleTV | Apple TV+ | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/AppleTV.lsr) |
| Bahamut | 巴哈姆特动画 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Bahamut.lsr) |
| Claude | Claude AI | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Claude.lsr) |
| Copilot | GitHub Copilot | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Copilot.lsr) |
| Disney | Disney+ | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Disney.lsr) |
| Emby | Emby 媒体服务器 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Emby.lsr) |
| Facebook | Facebook | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Facebook.lsr) |
| Game | 游戏平台 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Game.lsr) |
| Gemini | Google Gemini | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Gemini.lsr) |
| GitHub | GitHub | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/GitHub.lsr) |
| Google | Google 服务 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Google.lsr) |
| GoogleFCM | Google FCM 推送 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/GoogleFCM.lsr) |
| HBO | HBO Max | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/HBO.lsr) |
| Instagram | Instagram | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Instagram.lsr) |
| LAN_SPLITTER | 局域网分流 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/LAN_SPLITTER.lsr) |
| Microsoft | Microsoft 服务 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Microsoft.lsr) |
| Netflix | Netflix | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Netflix.lsr) |
| OpenAI | OpenAI/ChatGPT | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/OpenAI.lsr) |
| PrimeVideo | Amazon Prime Video | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/PrimeVideo.lsr) |
| REGION_SPLITTER | 地区分流 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/REGION_SPLITTER.lsr) |
| Speedtest | Speedtest 测速 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Speedtest.lsr) |
| Spotify | Spotify | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Spotify.lsr) |
| Steam | Steam 游戏平台 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Steam.lsr) |
| Telegram | Telegram | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Telegram.lsr) |
| TikTok | TikTok | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/TikTok.lsr) |
| Twitter | Twitter/X | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Twitter.lsr) |
| YouTube | YouTube | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/YouTube.lsr) |

### Clash 规则（9 项）

| 规则名称 | 用途 | Raw 链接 |
|---------|------|---------|
| AI | AI 服务聚合 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/AI.yaml) |
| Direct | 直连规则 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/Direct.yaml) |
| ESET_China | ESET 中国 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/ESET_China.yaml) |
| Game | 游戏平台 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/Game.yaml) |
| LAN | 局域网 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/LAN.yaml) |
| Netflix | Netflix | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/Netflix.yaml) |
| Proxy | 代理规则 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/Proxy.yaml) |
| SpeedtestInternational | 国际测速 | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/SpeedtestInternational.yaml) |
| TikTok | TikTok | [链接](https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/TikTok.yaml) |

## 📝 使用方法

### Loon

```ini
[Remote Rule]
https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/Netflix.lsr, policy=Netflix, tag=Netflix, enabled=true
```

### Clash

```yaml
rule-providers:
  Netflix:
    type: http
    behavior: classical
    url: https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/Netflix.yaml
    path: ./ruleset/Netflix.yaml
    interval: 86400
```

## 致谢

感谢 [iKeLee](https://iKeLee.one) 提供优质规则。
