"""
统一配置文件 - 所有脚本共享

MAINTENANCE NOTE (2026-10-08)
  实际生效的是两处：
    - CLASH_RULES          → upstream/scripts/sync_upstream_rules.py 读取
    - LOON_REMOTE_SOURCES  → 硬编码在 sync_upstream_rules.py 内（本文件不含 Loon 清单）
  以下内容为历史残留、当前没有任何实现，改动无效：
    LOON_RULES / BM7_RULES / YUUMIMI_RULES / AI_SOURCES /
    UPSTREAM_BM7 / UPSTREAM_YUUMIMI 及所有 *_SOURCE.txt 路径常量。
  新增规则集必须 CLASH_RULES 与 sync_upstream_rules.py 的
  LOON_REMOTE_SOURCES 同时登记，否则会产生孤儿文件。
"""

from pathlib import Path

# ==================== 路径配置 ====================
# 项目根目录（自动检测）
ROOT = Path(__file__).parent.parent.parent

# 自定义规则目录
CUSTOM_RULES = ROOT / "custom-rules"
CUSTOM_SCRIPTS = CUSTOM_RULES / "scripts"

# 上游规则目录
UPSTREAM = ROOT / "upstream"
UPSTREAM_LOON = UPSTREAM / "loon"
UPSTREAM_CORE = UPSTREAM / "core"
UPSTREAM_BM7 = UPSTREAM / "blackmatrix7"
UPSTREAM_YUUMIMI = UPSTREAM / "yuumimi"

# ==================== 本地规则配置 ====================
# Loon 本地规则
LOON_DIRECT_SRC = CUSTOM_RULES / "self-use-loon-source.txt"
LOON_DIRECT_DST = CUSTOM_RULES / "self-use-loon-rules.lsr"

LOON_PROXY_SRC = CUSTOM_RULES / "self-use-proxy-loon-source.txt"
LOON_PROXY_DST = CUSTOM_RULES / "self-use-proxy-loon-rules.lsr"

# OpenClash 本地规则
OC_DIRECT_SRC = CUSTOM_RULES / "self-use-openclash-source.txt"
OC_DIRECT_DST = CUSTOM_RULES / "self-use-openclash-rules.yaml"

OC_PROXY_SRC = CUSTOM_RULES / "self-use-proxy-openclash-source.txt"
OC_PROXY_DST = CUSTOM_RULES / "self-use-proxy-openclash-rules.yaml"

# Emby 规则
EMBY_SRC = CUSTOM_RULES / "urls.txt"
EMBY_LSR = CUSTOM_RULES / "Emby.lsr"
EMBY_YAML = CUSTOM_RULES / "Emby.yaml"

# Scattered 规则
SCATTERED_SRC = CUSTOM_RULES / "custom-scattered-source.txt"
SCATTERED_LIST = CUSTOM_RULES / "custom-scattered-rules.list"
SCATTERED_LSR = CUSTOM_RULES / "custom-scattered-rules.lsr"

# ==================== 上游同步配置 ====================
# iKeLee Loon 规则（20 项 - 核心精简版）
LOON_RULES = [
    # 基础（2 项）
    'LAN_SPLITTER', 'REGION_SPLITTER',
    # AI（4 项）
    'AI', 'OpenAI', 'Claude', 'Gemini',
    # 流媒体（4 项）
    'Netflix', 'Disney', 'YouTube', 'Spotify',
    # 社交（4 项）
    'Telegram', 'Twitter', 'Facebook', 'Instagram',
    # 平台（5 项）
    'Apple', 'Google', 'Microsoft', 'GitHub', 'TikTok',
    # 其他（1 项）
    'Game',
]

# iKeLee Clash 规则（11 项 - 核心精简版）
CLASH_RULES = {  # NEW_BATCH_2026_10
    # 文件内明确给出的规则（8 项）
    'LAN': 'https://kelee.one/Tool/Clash/Rule/LAN_SPLITTER.yaml',
    'Direct': 'https://kelee.one/Tool/Clash/Rule/Direct.yaml',
    'Proxy': 'https://kelee.one/Tool/Clash/Rule/Proxy.yaml',
    'AI': 'https://kelee.one/Tool/Clash/Rule/AI.yaml',
    'TikTok': 'https://kelee.one/Tool/Clash/Rule/TikTok.yaml',
    'Game': 'https://kelee.one/Tool/Clash/Rule/Game.yaml',
    'Netflix': 'https://rule.kelee.one/Clash/Netflix.yaml',
    'ESET_China': 'https://kelee.one/Tool/Clash/Rule/ESET_China.yaml',
    # 文件里没有的，参考 luestr/ShuntRules（3 项）
    'Telegram': 'https://rule.kelee.one/Clash/Telegram.yaml',
    'Google': 'https://rule.kelee.one/Clash/Google.yaml',
    'Apple': 'https://rule.kelee.one/Clash/Apple.yaml',
    # 常见规则补充（9 项）
    'YouTube': 'https://rule.kelee.one/Clash/YouTube.yaml',
    'Disney': 'https://rule.kelee.one/Clash/Disney.yaml',
    'Twitter': 'https://rule.kelee.one/Clash/Twitter.yaml',
    'Facebook': 'https://rule.kelee.one/Clash/Facebook.yaml',
    'Instagram': 'https://rule.kelee.one/Clash/Instagram.yaml',
    'Spotify': 'https://rule.kelee.one/Clash/Spotify.yaml',
    'GitHub': 'https://rule.kelee.one/Clash/GitHub.yaml',
    'Microsoft': 'https://rule.kelee.one/Clash/Microsoft.yaml',
    'Steam': 'https://rule.kelee.one/Clash/Steam.yaml',
    # --- 2026-10-08 用户指定扩充（两侧同加，勿单边）---
    'PayPal': 'https://rule.kelee.one/Clash/PayPal.yaml',
    'Amazon': 'https://rule.kelee.one/Clash/Amazon.yaml',
    'WeChat': 'https://rule.kelee.one/Clash/WeChat.yaml',
    'Weibo': 'https://rule.kelee.one/Clash/Weibo.yaml',
    'Bing': 'https://rule.kelee.one/Clash/Bing.yaml',
    'Twitch': 'https://rule.kelee.one/Clash/Twitch.yaml',
}

# blackmatrix7 规则（13 项）
BM7_RULES = [
    "Apple", "YouTube", "GitHub", "Google", "Microsoft",
    "Telegram", "Twitter", "Discord", "Steam", "Emby",
    "PayPal", "Speedtest", "Scholar"
]

# yuumimi 规则（12 项）
YUUMIMI_RULES = [
    "apple", "youtube", "github", "google", "microsoft",
    "telegram", "twitter", "discord", "steam", "paypal",
    "speedtest", "category-scholar-!cn"
]

# ==================== 网络请求配置 ====================
# User-Agent
UA_LOON = 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0'
UA_CLASH = 'clash.meta'
UA_MINIS = 'minis'

# 请求延迟（秒）
DELAY_LOON = (2, 5)    # Loon 规则请求延迟范围
DELAY_CLASH = (2, 5)   # Clash 规则请求延迟范围
DELAY_BM7 = (1, 3)     # blackmatrix7 规则请求延迟范围

# 重试配置
RETRY_TIMES = 4        # 重试次数
RETRY_PAUSE = 6        # 重试间隔基础值（秒）

# ==================== 同步报告配置 ====================
SYNC_REPORT = UPSTREAM / "_sync_report.json"
SYNC_SCHEDULE = "external scheduler; run upstream/scripts/local_sync_and_push.py"

# ==================== AI 聚合配置 ====================
AI_SOURCES = [
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BardAI/BardAI.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Anthropic/Anthropic.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Claude/Claude.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Copilot/Copilot.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Gemini/Gemini.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Jetbrains/Jetbrains.yaml',
    'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/aiXcoder/aiXcoder.yaml',
]
