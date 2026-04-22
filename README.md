# Profiles

这个仓库用于存放我自己的配置模板与自用规则生成文件。

## 当前主用
- `templates/openclash/openclash-template-kelee-style.yaml`
- `custom-rules/self-use-loon-rules.lsr`
- `custom-rules/self-use-openclash-rules.yaml`
- `custom-rules/self-use-proxy-loon-rules.lsr`
- `custom-rules/self-use-proxy-openclash-rules.yaml`

## 上游镜像结构
- 基础骨架：`upstream/ShuntRules/`
- 主规则源：`upstream/blackmatrix7/`
- 补规则源：`upstream/yuumimi/`
- 同步报告：`upstream/_sync_report.json`

## 维护入口
- Loon 自用直连源：`custom-rules/self-use-loon-source.txt`
- OpenClash 自用直连源：`custom-rules/self-use-openclash-source.txt`
- Loon 自用代理源：`custom-rules/self-use-proxy-loon-source.txt`
- OpenClash 自用代理源：`custom-rules/self-use-proxy-openclash-source.txt`

## 规则边界
- Loon 只保留 `.lsr` 自用产物；上游镜像保留 `.list`
- OpenClash 只保留 `.yaml` 自用产物
- `source.txt` 改动后自动生成自用规则
- 上游规则按定时 workflow 自动同步
- `Game` 使用完整上游规则，不再做 foreign 过滤

## 当前同步范围
- ShuntRules：`LAN / Direct / Proxy / AI / Game / Netflix / ESET_China`
- blackmatrix7：`Apple / YouTube / GitHub / Google / Microsoft / Telegram / Twitter / Discord / Steam / Emby / PayPal / Speedtest / Scholar`
- yuumimi：`Apple / YouTube / GitHub / Google / Microsoft / Telegram / Twitter / Discord / Steam / PayPal / Speedtest / Scholar`

## 自动生成
- `update_self_use_rules.py`
- `sync_upstream_rules.py`

## 上游来源声明
- `upstream/ShuntRules/` 来源：`cc166/ShuntRules`
- `upstream/blackmatrix7/` 来源：`blackmatrix7/ios_rule_script`
- `upstream/yuumimi/` 来源：`yuumimi/rules`（基于其规则生成思路在本仓库内生成补源产物）
