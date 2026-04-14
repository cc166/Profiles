from pathlib import Path

SRC = Path('custom-rules/custom-scattered-source.txt')
DST_LIST = Path('custom-rules/custom-scattered-rules.list')
DST_LSR = Path('custom-rules/custom-scattered-rules.lsr')

if not SRC.exists():
    raise SystemExit('missing source file: custom-rules/custom-scattered-source.txt')

seen = set()
out = ['# Custom Scattered Rules', '# Generated from custom-scattered-source.txt', '']

for raw in SRC.read_text(encoding='utf-8').splitlines():
    line = raw.rstrip()
    stripped = line.strip()
    if not stripped:
        out.append('')
        continue
    if stripped.startswith('#') and not stripped.startswith('#DOMAIN') and not stripped.startswith('#DOMAIN-SUFFIX'):
        out.append(line)
        continue

    commented = False
    work = stripped
    if work.startswith('#'):
        commented = True
        work = work[1:]

    parts = [p.strip() for p in work.split(',') if p.strip()]
    if not parts:
        out.append(line)
        continue

    rule_type = parts[0].upper()
    if rule_type not in ('DOMAIN', 'DOMAIN-SUFFIX'):
        out.append(line)
        continue

    if len(parts) == 2:
        domain = parts[1].lower()
        policy = 'DIRECT'
    else:
        domain = parts[1].lower()
        policy = parts[2].upper()

    normalized = f'{rule_type},{domain},{policy}'
    key = ('#' if commented else '') + normalized
    if key in seen:
        continue
    seen.add(key)
    out.append(('#' if commented else '') + normalized)

text = '\n'.join(out).rstrip() + '\n'
DST_LIST.write_text(text, encoding='utf-8')
DST_LSR.write_text(text, encoding='utf-8')
print('updated', DST_LIST, DST_LSR)
