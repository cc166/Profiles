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
- `upstream/core/` 当前来源：已部分切到 iKeLee 可验证源；其中 `Direct / Game / Netflix` 已直连同步，`LAN / AI / ESET_China` 暂保留过渡来源
- `upstream/blackmatrix7/` 来源：`blackmatrix7/ios_rule_script`
- `upstream/yuumimi/` 来源：`yuumimi/rules`（基于其规则生成思路在本仓库内生成补源产物）

- `upstream/core/` 当前已直接切到 iKeLee 可验证源：`Direct / Game / Netflix`；`LAN / AI / ESET_China` 仍待确认真实规则名后再切
