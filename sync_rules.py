"""
自用规则自动同步脚本
功能：修改一个同名的 .lsr 或 .yaml，另一个自动同步规则内容
"""

from pathlib import Path
import re

# 项目根目录
ROOT = Path(__file__).parent.parent.parent
CUSTOM_RULES = ROOT / "custom-rules"

def parse_loon_rule(line):
    """解析 Loon 规则行，返回 (type, value) 或 None"""
    line = line.strip()
    if not line or line.startswith('#') or line.startswith('//') or line.startswith(';'):
        return None
    
    parts = [p.strip() for p in line.split(',') if p.strip()]
    if len(parts) >= 2 and parts[0].upper() in ('DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR', 'IP-CIDR6', 'IP-ASN', 'USER-AGENT', 'URL-REGEX', 'GEOIP'):
        return (parts[0].upper(), parts[1].lower() if parts[0].upper() in ('DOMAIN', 'DOMAIN-SUFFIX') else parts[1])
    return None

def parse_clash_rule(line):
    """解析 Clash 规则行，返回 (type, value) 或 None"""
    line = line.strip()
    if not line or line.startswith('#') or line == 'payload:':
        return None
    
    # Clash 格式：  - "DOMAIN-SUFFIX,example.com"
    if line.startswith('- '):
        content = line[2:].strip().strip('"').strip("'")
        parts = [p.strip() for p in content.split(',') if p.strip()]
        if len(parts) >= 2:
            rule_type = parts[0].upper()
            value = parts[1].lower() if rule_type in ('DOMAIN', 'DOMAIN-SUFFIX') else parts[1]
            return (rule_type, value)
    return None

def loon_to_clash(loon_file, clash_file):
    """从 Loon .lsr 生成 Clash .yaml"""
    rules = []
    for line in loon_file.read_text(encoding='utf-8').splitlines():
        parsed = parse_loon_rule(line)
        if parsed:
            rule_type, value = parsed
            rules.append(f'  - "{rule_type},{value}"')
    
    output = ['payload:'] + rules
    clash_file.write_text('\n'.join(output) + '\n', encoding='utf-8')

def clash_to_loon(clash_file, loon_file):
    """从 Clash .yaml 生成 Loon .lsr"""
    rules = []
    for line in clash_file.read_text(encoding='utf-8').splitlines():
        parsed = parse_clash_rule(line)
        if parsed:
            rule_type, value = parsed
            rules.append(f'{rule_type},{value}')
    
    loon_file.write_text('\n'.join(rules) + '\n', encoding='utf-8')

def sync_rules():
    """同步所有同名规则文件"""
    synced = []
    
    # 查找所有 .lsr 和 .yaml 文件
    lsr_files = list(CUSTOM_RULES.glob('*.lsr'))
    yaml_files = list(CUSTOM_RULES.glob('*.yaml'))
    
    for lsr_file in lsr_files:
        yaml_file = lsr_file.with_suffix('.yaml')
        if yaml_file.exists():
            # 比较修改时间，同步较新的到较旧的
            if lsr_file.stat().st_mtime > yaml_file.stat().st_mtime:
                loon_to_clash(lsr_file, yaml_file)
                synced.append(f'{lsr_file.name} → {yaml_file.name}')
            elif yaml_file.stat().st_mtime > lsr_file.stat().st_mtime:
                clash_to_loon(yaml_file, lsr_file)
                synced.append(f'{yaml_file.name} → {lsr_file.name}')
    
    return synced

if __name__ == '__main__':
    synced = sync_rules()
    if synced:
        print(f'✅ 同步完成（{len(synced)} 对）：')
        for item in synced:
            print(f'  - {item}')
    else:
        print('✅ 所有同名规则文件已是最新')
