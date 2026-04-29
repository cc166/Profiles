from pathlib import Path
import re

LOON_SRC = Path('custom-rules/self-use-loon-source.txt')
OC_SRC = Path('custom-rules/self-use-openclash-source.txt')
PROXY_LOON_SRC = Path('custom-rules/self-use-proxy-loon-source.txt')
PROXY_OC_SRC = Path('custom-rules/self-use-proxy-openclash-source.txt')

LOON_LSR = Path('custom-rules/self-use-loon-rules.lsr')
OC_YAML = Path('custom-rules/self-use-openclash-rules.yaml')
PROXY_LOON_LSR = Path('custom-rules/self-use-proxy-loon-rules.lsr')
PROXY_OC_YAML = Path('custom-rules/self-use-proxy-openclash-rules.yaml')

def norm_rule_line(s):
    parts=[p.strip() for p in s.split(',') if p.strip()]
    if len(parts)>=2 and parts[0].upper() in ('DOMAIN','DOMAIN-SUFFIX'):
        policy = parts[2].upper() if len(parts)>=3 else ''
        return parts[0].upper(), parts[1].lower(), policy
    return None

def gen_loon_direct(src_text):
    out=['# Self Use Rules For Loon','# Generated from self-use-loon-source.txt','']
    seen=set()
    for raw in src_text.splitlines():
        line=raw.rstrip(); s=line.strip()
        if not s:
            out.append(''); continue
        if s.startswith('#'):
            out.append(line); continue
        if s.startswith('http://') or s.startswith('https://'):
            m=re.findall(r'https?://([^:/ \n\r]+)', s)
            for d in m:
                d=d.lower(); rule=('DOMAIN,'+d) if d.count('.')>1 else ('DOMAIN-SUFFIX,'+d)
                final=rule+',DIRECT'
                if final not in seen:
                    seen.add(final); out.append(final)
            continue
        nr=norm_rule_line(s)
        if nr:
            final=f'{nr[0]},{nr[1]},{nr[2] or "DIRECT"}'
            if final not in seen:
                seen.add(final); out.append(final)
        else:
            out.append(line)
    return '\n'.join(out).rstrip()+'\n'

def gen_yaml(src_text, title):
    out=['payload:', f'# {title}']
    seen=set()
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
    return '\n'.join(out).rstrip()+'\n'

def gen_loon_proxy(src_text):
    out=['# Self Use Proxy Rules For Loon','# Generated from self-use-proxy-loon-source.txt','']
    seen=set()
    for raw in src_text.splitlines():
        line=raw.rstrip(); s=line.strip()
        if not s:
            out.append(''); continue
        if s.startswith('#'):
            out.append(line); continue
        nr=norm_rule_line(s)
        if nr:
            final=f'{nr[0]},{nr[1]},{nr[2] or "PROXY"}'
            if final not in seen:
                seen.add(final); out.append(final)
        else:
            out.append(line)
    return '\n'.join(out).rstrip()+'\n'

LOON_LSR.write_text(gen_loon_direct(LOON_SRC.read_text(encoding='utf-8', errors='ignore')), encoding='utf-8')
OC_YAML.write_text(gen_yaml(OC_SRC.read_text(encoding='utf-8', errors='ignore'), 'Self Use Rules For OpenClash'), encoding='utf-8')
PROXY_LOON_LSR.write_text(gen_loon_proxy(PROXY_LOON_SRC.read_text(encoding='utf-8', errors='ignore')), encoding='utf-8')
PROXY_OC_YAML.write_text(gen_yaml(PROXY_OC_SRC.read_text(encoding='utf-8', errors='ignore'), 'Self Use Proxy Rules For OpenClash'), encoding='utf-8')
print('generated minimal self use direct/proxy rules')
