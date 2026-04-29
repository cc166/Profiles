# cc166/Profiles - iKeLee 规则镜像

完整镜像 iKeLee 规则，每 2 天自动同步一次。

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

## 🔄 同步策略

- **同步频率**：每 2 天一次（UTC 03:23 = 北京时间 11:23）
- **规则来源**：iKeLee 官方（rule.kelee.one 和 kelee.one）
- **Cloudflare 绕过**：已优化（浏览器特征 Headers + 随机延迟）
- **保底机制**：`last-known-good` 策略，拉取失败时保留现有文件

## 📝 使用方法

### Loon
```
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

## 🔗 相关仓库

- **主用**：[cc166/Profiles](https://github.com/cc166/Profiles) - iKeLee 规则镜像（本仓库）
- **备用**：[cc166/ShuntRules](https://github.com/cc166/ShuntRules) - 自动跟随 luestr/ShuntRules
- **上游**：[iKeLee 规则](https://rule.kelee.one/) - 官方规则源

## 📊 同步报告

查看最近一次同步结果：[_sync_report.json](https://github.com/cc166/Profiles/blob/master/upstream/_sync_report.json)
