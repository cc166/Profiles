# Profiles

个人 Loon 和 Clash 配置仓库。

## 规则列表

完整规则列表请查看 [RULES.md](RULES.md)

- **Loon 规则**：32 项
- **Clash 规则**：9 项

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

## 致谢

感谢 [iKeLee](https://iKeLee.one) 提供优质规则。

## License

MIT
