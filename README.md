# Profiles

这个仓库用于存放我自己的配置模板与自用规则生成文件。

## 当前主用
- `templates/openclash/openclash-template-kelee-style.yaml`
- `custom-rules/self-use-loon-rules.lsr`
- `custom-rules/self-use-openclash-rules.yaml`
- `custom-rules/self-use-proxy-loon-rules.lsr`
- `custom-rules/self-use-proxy-openclash-rules.yaml`
- `custom-rules/game-foreign-rules.yaml`

## 维护入口
- Loon 自用直连源：`custom-rules/self-use-loon-source.txt`
- OpenClash 自用直连源：`custom-rules/self-use-openclash-source.txt`
- Loon 自用代理源：`custom-rules/self-use-proxy-loon-source.txt`
- OpenClash 自用代理源：`custom-rules/self-use-proxy-openclash-source.txt`

## 规则边界
- Loon 只保留 `.lsr` 生成物
- OpenClash 只保留 `.yaml` 生成物
- 改 `source.txt` 后由 workflow 自动生成对应产物
- `game-foreign-rules.yaml` 只保留偏国外游戏平台 / 海外游戏域名

## 自动生成
- `update_self_use_rules.py`

## 上游镜像同步
- workflow：`.github/workflows/sync-upstream-rules.yml`
- 脚本：`sync_upstream_rules.py`
- 当前镜像目录：`upstream/ShuntRules/`
- 用途：定时/手动把上游规则文件同步进本仓库，便于固定引用与留存历史

- 当前镜像范围：LAN / Direct / Proxy / AI / Game / Netflix / YouTube / Apple / Microsoft / Google / GitHub / Telegram / Twitter / Discord / Steam / Emby / PayPal / Speedtest / Scholar / ProxyMedia / ESET_China

- 同步策略：单文件失败不终止整轮，同步结果写入 `upstream/ShuntRules/_sync_report.json`

## 上游镜像策略
- 主规则源：`blackmatrix7/ios_rule_script`
- 补充规则源：`yuumimi/rules`
- 兼容保留：`ShuntRules`
- OpenClash 优先使用镜像到仓库内的 `.yaml`
- Loon / 其他 iOS 代理优先使用镜像到仓库内的 `.list` / `.lsr`
