"""
统一配置文件 - 所有脚本共享
修改此文件后，其他脚本自动生效
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

# ==================== 自用规则配置 ====================
# Loon 自用规则
LOON_DIRECT_SRC = CUSTOM_RULES / "self-use-loon-source.txt"
LOON_DIRECT_DST = CUSTOM_RULES / "self-use-loon-rules.lsr"

LOON_PROXY_SRC = CUSTOM_RULES / "self-use-proxy-loon-source.txt"
LOON_PROXY_DST = CUSTOM_RULES / "self-use-proxy-loon-rules.lsr"

# OpenClash 自用规则
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

# iKeLee Clash 规则（10 项 - 核心精简版）
CLASH_RULES = {
    # 基础规则（4 项）
    'Direct': 'https://rule.kelee.one/Clash/Direct.yaml',
    'Proxy': 'https://kelee.one/Tool/Clash/Rule/Proxy.yaml',
    'LAN': 'https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/LAN.yaml',
    'ESET_China': 'https://raw.githubusercontent.com/cc166/ShuntRules/main/mirror/ClashCore/ESET_China.yaml',
    # 核心服务（6 项）
    'AI': None,  # 由 blackmatrix7 8 项聚合生成
    'Netflix': 'https://rule.kelee.one/Clash/Netflix.yaml',
    'Telegram': 'https://kelee.one/Tool/Clash/Rule/Telegram.yaml',
    'Google': 'https://kelee.one/Tool/Clash/Rule/Google.yaml',
    'Apple': 'https://kelee.one/Tool/Clash/Rule/Apple.yaml',
    'TikTok': 'https://kelee.one/Tool/Clash/Rule/TikTok.yaml',
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
SYNC_SCHEDULE = "sync-upstream-rules.yml cron 23 3 * * * (UTC, daily)"

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
