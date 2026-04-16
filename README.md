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
