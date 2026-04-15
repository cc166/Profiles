from pathlib import Path
import re

LOON_SRC = Path('custom-rules/self-use-loon-source.txt')
OC_SRC = Path('custom-rules/self-use-openclash-source.txt')
LOON_LST = Path('custom-rules/self-use-loon-rules.list')
LOON_LSR = Path('custom-rules/self-use-loon-rules.lsr')
OC_YAML = Path('custom-rules/self-use-openclash-rules.yaml')

def norm_rule_line(s):
    parts=[p.strip() for p in s.split(',') if p.strip()]
    if len(parts)>=2 and parts[0].upper() in ('DOMAIN','DOMAIN-SUFFIX'):
        return parts[0].upper(), parts[1].lower()
    return None

def gen_loon(src_text):
    out=['# Self Use Rules For Loon','# Generated from self-use-loon-source.txt','']
    seen=set(); section=''
    for raw in src_text.splitlines():
        line=raw.rstrip(); s=line.strip()
        if not s:
            out.append(''); continue
        if s.startswith('#') and not s.startswith('## '):
            out.append(line); continue
        if s.startswith('## '):
            out.append('# ' + s[3:].strip()); section=s[3:].strip().lower(); continue
        if section=='emby':
            domains=re.findall(r'https?://([^:/ 
]+)', s)
            for d in domains:
                d=d.lower(); rule=('DOMAIN,'+d) if d.count('.')>1 else ('DOMAIN-SUFFIX,'+d)
                final=rule+',DIRECT'
                if final not in seen:
                    seen.add(final); out.append(final)
            continue
        nr=norm_rule_line(s)
        if nr:
            final=f'{nr[0]},{nr[1]},DIRECT'
            if final not in seen:
                seen.add(final); out.append(final)
        else:
            out.append(line)
    text='
'.join(out).rstrip()+'
'
    LOON_LST.write_text(text, encoding='utf-8')
    LOON_LSR.write_text(text, encoding='utf-8')

def gen_oc(src_text):
    out=['payload:']; seen=set()
    for raw in src_text.splitlines():
        line=raw.rstrip(); s=line.strip()
        if not s:
            out.append(''); continue
        if s.startswith('#'):
            out.append(line); continue
        nr=norm_rule_line(s)
        if nr:
            rule=f'{nr[0]},{nr[1]}'
            if rule not in seen:
                seen.add(rule); out.append('  - ' + rule)
        else:
            out.append(line)
    OC_YAML.write_text('
'.join(out).rstrip()+'
', encoding='utf-8')

gen_loon(LOON_SRC.read_text(encoding='utf-8', errors='ignore'))
gen_oc(OC_SRC.read_text(encoding='utf-8', errors='ignore'))
print('generated separate loon/openclash self-use rules')
