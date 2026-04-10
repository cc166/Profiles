# OpenClash 模板说明

## 关于订阅部分

如果你使用的是 OpenClash 的订阅转换：
- 这个模板里不需要保留复杂的 iKeLee 多订阅锚点结构
- 现在模板里只保留了一个最小占位 provider，方便你替换
- 你也可以直接删掉这个占位 provider，然后让订阅转换结果来注入节点

## 不删会不会影响
- 不会致命影响
- 但会显得多余
- 最干净的做法是：
  - 要么改成你自己的订阅转换结果 URL
  - 要么直接删除这个占位 provider

## 当前模板取舍
- 保留 iKeLee 的框架和设置
- 去掉他那套自动地区优选作为核心
- 策略组改得更精简
- ChatGPT 已并入 AI 服务
- DisneyPlus / HBO / PrimeVideo / Emby / Bahamut 不再单独分组，统一走兜底媒体/漏网之鱼
- 直连规则与 `ESET_China -> DIRECT` 建议继续沿用原作者规则
