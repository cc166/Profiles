from pathlib import Path
import re

SRC = Path('custom-rules/self-use-source.txt')
DST_LIST = Path('custom-rules/self-use-rules.list')
DST_LSR = Path('custom-rules/self-use-rules.lsr')
DST_YAML = Path('custom-rules/self-use-rules.yaml')

text = SRC.read_text(encoding='utf-8', errors='ignore')
lines = text.splitlines()

out_list = ['# Self Use Rules', '# Generated from self-use-source.txt', '']
out_yaml = ['payload:']
seen_list = set()
seen_yaml = set()
section = ''
for raw in lines:
    line = raw.rstrip()
    s = line.strip()
    if not s:
        out_list.append('')
        out_yaml.append('')
        continue
    if s.startswith('## '):
        section = s[3:].strip().lower()
        out_list.append('# ' + s[3:].strip())
        out_yaml.append('# ' + s[3:].strip())
        continue
    if s.startswith('#'):
        out_list.append(line)
        out_yaml.append(line)
        continue
    if section == 'emby':
        m = re.findall(r'https?://([^:/ 
]+)', s)
        for domain in m:
            domain = domain.lower()
            rule = ('DOMAIN,' + domain) if domain.count('.') > 1 else ('DOMAIN-SUFFIX,' + domain)
            list_rule = rule + ',DIRECT'
            if list_rule not in seen_list:
                seen_list.add(list_rule)
                out_list.append(list_rule)
            if rule not in seen_yaml:
                seen_yaml.add(rule)
                out_yaml.append('  - ' + rule)
        continue
    parts = [p.strip() for p in s.split(',') if p.strip()]
    if len(parts) >= 2 and parts[0].upper() in ('DOMAIN','DOMAIN-SUFFIX'):
        rule = f"{parts[0].upper()},{parts[1].lower()}"
        list_rule = rule + ',DIRECT'
        if list_rule not in seen_list:
            seen_list.add(list_rule)
            out_list.append(list_rule)
        if rule not in seen_yaml:
            seen_yaml.add(rule)
            out_yaml.append('  - ' + rule)
    else:
        out_list.append(line)

text_list='
'.join(out_list).rstrip()+'
'
DST_LIST.write_text(text_list, encoding='utf-8')
DST_LSR.write_text(text_list, encoding='utf-8')
DST_YAML.write_text('
'.join(out_yaml).rstrip()+'
', encoding='utf-8')
print('generated self-use rules')
