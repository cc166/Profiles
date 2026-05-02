# Profiles

个人 Loon 和 Clash 配置仓库。

## 使用方法

### Loon

在配置文件的 `[Remote Rule]` 部分添加：

```ini
https://raw.githubusercontent.com/cc166/Profiles/master/upstream/loon/规则名.lsr, policy=策略组, tag=标签, enabled=true
```

### Clash

在配置文件的 `rule-providers` 部分添加对应规则：

```yaml
rule-providers:
  规则名:
    type: http
    behavior: classical
    url: https://raw.githubusercontent.com/cc166/Profiles/master/upstream/core/规则名.yaml
    path: ./ruleset/规则名.yaml
    interval: 86400
```

## 规则列表

完整规则列表请查看 [RULES.md](RULES.md)


## 维护

上游规则镜像由自托管 VM 上的 systemd timer 定时同步并推送，GitHub Actions 不再负责拉取上游。

手动同步入口保留为：

```bash
python3 upstream/scripts/local_sync_and_push.py
```

生成的 `upstream/_sync_report*.json` 仅用于本地运行校验，不纳入版本库。

## 致谢

感谢 [iKeLee](https://iKeLee.one) 提供优质规则。

## License

MIT
