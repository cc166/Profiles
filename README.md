# Profiles

这个仓库用于存放我自己的配置模板与自用规则生成文件。

## 当前主用
- `templates/openclash/openclash-template-kelee-style.yaml`
- `custom-rules/self-use-loon-rules.lsr`
- `custom-rules/self-use-openclash-rules.yaml`
- `custom-rules/self-use-proxy-loon-rules.lsr`
- `custom-rules/self-use-proxy-openclash-rules.yaml`

## 上游镜像结构
- 一比一复刻骨架：`upstream/core/`（`LAN` 已内联进主配置，不再单独分发）
- 主规则源：`upstream/blackmatrix7/`
- 补规则源：`upstream/yuumimi/`
- 同步报告：`upstream/_sync_report.json`

## 维护入口
- Loon 自用直连源：`custom-rules/self-use-loon-source.txt`
- OpenClash 自用直连源：`custom-rules/self-use-openclash-source.txt`
- Loon 自用代理源：`custom-rules/self-use-proxy-loon-source.txt`
- OpenClash 自用代理源：`custom-rules/self-use-proxy-openclash-source.txt`

## 规则边界
- `upstream/core/` 用于一比一复刻当前基础骨架规则；后续一旦拿到 iKeLee 可验证直连源，可直接替换同步来源而不改引用路径
- 主源：`blackmatrix7/ios_rule_script`
- 补源：`yuumimi/rules`（基于其规则生成思路在本仓库内生成补源产物）
- `Game` 使用完整上游规则，不再做 foreign 过滤

## 当前同步范围
- core：`Direct / AI / Game / Netflix / ESET_China`（`LAN` 已直接内联）
- blackmatrix7：`Apple / YouTube / GitHub / Google / Microsoft / Telegram / Twitter / Discord / Steam / Emby / PayPal / Speedtest / Scholar`
- yuumimi：`Apple / YouTube / GitHub / Google / Microsoft / Telegram / Twitter / Discord / Steam / PayPal / Speedtest / Scholar`

## 自动生成
- `update_self_use_rules.py`
- `sync_upstream_rules.py`

## 上游来源声明
- `upstream/core/Direct / Game / Netflix`：`https://rule.kelee.one/Clash/*.yaml`（iKeLee 可验证源）
- `upstream/core/AI`：由 `blackmatrix7/ios_rule_script` 的 `OpenAI / BardAI / Anthropic / Claude / Copilot / Gemini / Jetbrains / aiXcoder` 8 个规则聚合生成
- `upstream/core/ESET_China`：暂沿用 `cc166/ShuntRules` 过渡静态源
- `LAN`：已内联进主配置，不再单独分发
- `upstream/blackmatrix7/` 来源：`blackmatrix7/ios_rule_script`
- `upstream/yuumimi/` 来源：`yuumimi/rules`（基于其规则生成思路在本仓库内生成补源产物）

## Loon 可直接替换的规则链接
- 自用直连：`https://raw.githubusercontent.com/cc166/Profiles/master/custom-rules/self-use-loon-rules.lsr`
- 自用代理：`https://raw.githubusercontent.com/cc166/Profiles/master/custom-rules/self-use-proxy-loon-rules.lsr`
- Direct：`https://rule.kelee.one/Loon/Direct.lsr`
- Game：`https://rule.kelee.one/Loon/Game.lsr`
- Netflix：`https://rule.kelee.one/Loon/Netflix.lsr`
- AI（建议改为分项组合，不主用 iKeLee 总聚合）：
  - OpenAI：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/OpenAI/OpenAI.list`
  - BardAI：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/BardAI/BardAI.list`
  - Anthropic：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Anthropic/Anthropic.list`
  - Claude：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Claude/Claude.list`
  - Copilot：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Copilot/Copilot.list`
  - Gemini：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Gemini/Gemini.list`
  - Jetbrains：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Jetbrains/Jetbrains.list`
  - aiXcoder：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/aiXcoder/aiXcoder.list`
- 常用分项（bm7）：
  - Apple：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Apple/Apple.list`
  - YouTube：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/YouTube/YouTube.list`
  - GitHub：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/GitHub/GitHub.list`
  - Google：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Google/Google.list`
  - Microsoft：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Microsoft/Microsoft.list`
  - Telegram：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Telegram/Telegram.list`
  - Twitter：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Twitter/Twitter.list`
  - Discord：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Discord/Discord.list`
  - Steam：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Steam/Steam.list`
  - Emby：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Emby/Emby.list`
  - PayPal：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/PayPal/PayPal.list`
  - Speedtest：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Speedtest/Speedtest.list`
  - Scholar：`https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Scholar/Scholar.list`

## 同步保底策略
- 定时：`sync-upstream-rules.yml` 当前为 `23 3 */2 * *`（GitHub Actions cron，UTC，每 2 天一次）
- `Direct / Game / Netflix`：拉取失败时保留 last-known-good，不覆盖已验证文件
- `AI`：改为 `blackmatrix7` 8 源聚合，并保留 last-known-good；避免主走 iKeLee 频繁请求
- 以 `upstream/_sync_report.json` 为准：若出现 `kept_last_good: true` 或 `status: kept-last-known-good*`，表示本次抓取失败，但仓库中的正确文件已被保留
