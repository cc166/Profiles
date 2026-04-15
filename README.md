# Profiles

这个仓库用于存放我自己的配置模板与自用规则生成文件。

## 当前主用
- `templates/openclash/openclash-template-kelee-style.yaml`
- `custom-rules/self-use-loon-rules.lsr`
- `custom-rules/self-use-openclash-rules.yaml`
- `custom-rules/self-use-proxy-loon-rules.lsr`
- `custom-rules/self-use-proxy-openclash-rules.yaml`

## 维护入口
- Loon 自用直连源：`custom-rules/self-use-loon-source.txt`
- OpenClash 自用直连源：`custom-rules/self-use-openclash-source.txt`
- Loon 自用代理源：`custom-rules/self-use-proxy-loon-source.txt`
- OpenClash 自用代理源：`custom-rules/self-use-proxy-openclash-source.txt`

## 规则边界
- Loon 自用直连规则包含 Emby + 零散直连规则
- OpenClash 自用直连规则只包含零散直连规则，不带 Emby
- 代理规则单独维护，想代理的域名自己填进 proxy 源文件

## 自动生成
- `update_self_use_rules.py`

## 自用规则（分直连 / 代理，分 Loon / OpenClash）

### 自用直连
- Loon 源：`custom-rules/self-use-loon-source.txt`
- Loon 生成：`custom-rules/self-use-loon-rules.list`、`custom-rules/self-use-loon-rules.lsr`
- OpenClash 源：`custom-rules/self-use-openclash-source.txt`
- OpenClash 生成：`custom-rules/self-use-openclash-rules.yaml`

### 自用代理
- Loon 源：`custom-rules/self-use-proxy-loon-source.txt`
- Loon 生成：`custom-rules/self-use-proxy-loon-rules.list`、`custom-rules/self-use-proxy-loon-rules.lsr`
- OpenClash 源：`custom-rules/self-use-proxy-openclash-source.txt`
- OpenClash 生成：`custom-rules/self-use-proxy-openclash-rules.yaml`

