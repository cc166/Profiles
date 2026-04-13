import re
from pathlib import Path

# Emby Loon -> Clash
loon_lines = Path('Emby.lsr').read_text(encoding='utf-8', errors='ignore').splitlines()
emby_out = ['payload:']
seen = set()
for line in loon_lines:
    s = line.strip()
    if not s or s.startswith('#'):
        continue
    if s not in seen:
        seen.add(s)
        emby_out.append(f'  - {s}')
Path('Emby.yaml').write_text('\n'.join(emby_out) + '\n', encoding='utf-8')

# scattered source -> clash yaml
src = Path('custom-rules/custom-scattered-source.txt')
out = ['payload:']
seen = set()
for raw in src.read_text(encoding='utf-8', errors='ignore').splitlines():
    s = raw.strip()
    if not s or s.startswith('#'):
        continue
    parts = [p.strip() for p in s.split(',') if p.strip()]
    if len(parts) >= 2 and parts[0].upper() in ('DOMAIN', 'DOMAIN-SUFFIX'):
        rule = f"{parts[0].upper()},{parts[1].lower()}"
        if rule not in seen:
            seen.add(rule)
            out.append(f'  - {rule}')
Path('custom-rules/custom-scattered-rules.yaml').write_text('\n'.join(out) + '\n', encoding='utf-8')
print('generated Emby.yaml and custom-scattered-rules.yaml')
