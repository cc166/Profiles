import sys
from pathlib import Path

VALID = {
    'DOMAIN','DOMAIN-SUFFIX','DOMAIN-KEYWORD','IP-CIDR','IP-CIDR6','IP-ASN',
    'USER-AGENT','URL-REGEX','GEOIP','PROCESS-NAME','DST-PORT','SRC-IP-CIDR',
    'SRC-PORT','RULE-SET','DOMAIN-SET'
}

def fail(msg):
    print('ERROR:', msg)
    raise SystemExit(1)

for path in Path('custom-rules').glob('*.yaml'):
    lines = path.read_text(encoding='utf-8').splitlines()
    if not lines or lines[0].strip() != 'payload:':
        fail(f'{path}: first line must be payload:')
    count = 0
    for no, raw in enumerate(lines[1:], 2):
        s = raw.strip()
        if not s or s.startswith('#'):
            continue
        if not s.startswith('- '):
            fail(f'{path}:{no}: expected payload item, got {raw!r}')
        item = s[2:].strip().strip('"').strip("'")
        typ = item.split(',', 1)[0].upper()
        if typ not in VALID:
            fail(f'{path}:{no}: unknown rule type {typ}')
        count += 1
    print(f'OK {path}: {count} payload rule(s)')

for path in Path('custom-rules').glob('*.lsr'):
    count = 0
    for no, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith(('#','//',';')):
            continue
        typ = s.split(',', 1)[0].upper()
        if typ not in VALID:
            fail(f'{path}:{no}: unknown rule type {typ}')
        count += 1
    print(f'OK {path}: {count} rule(s)')
