#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / 'upstream' / 'scripts' / 'sync_upstream_rules.py'
REPORT = ROOT / 'upstream' / '_sync_report.json'

r = subprocess.run(['python3', str(SYNC)], cwd=ROOT)
if r.returncode != 0:
    raise SystemExit(r.returncode)
report = json.loads(REPORT.read_text(encoding='utf-8'))
core_ok = len(report['core']['ok'])
loon_ok = len(report['loon_remote']['ok'])
expected_core = report['meta']['expected_core']
expected_loon = report['meta']['expected_loon']
if core_ok != expected_core or loon_ok != expected_loon:
    raise SystemExit(f'incomplete upstream sync: core {core_ok}/{expected_core}, loon {loon_ok}/{expected_loon}')

subprocess.run(['git', 'add', 'upstream'], cwd=ROOT, check=True)
diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT)
if diff.returncode == 0:
    print('✅ upstream rules already up to date; nothing to push')
    raise SystemExit(0)

subprocess.run(['git', 'config', '--local', 'user.email', 'minis-local-sync@users.noreply.github.com'], cwd=ROOT, check=True)
subprocess.run(['git', 'config', '--local', 'user.name', 'minis-local-sync'], cwd=ROOT, check=True)
msg = f'chore: sync upstream rules (local) core {core_ok}/{expected_core}, loon {loon_ok}/{expected_loon}'
subprocess.run(['git', 'commit', '-m', msg], cwd=ROOT, check=True)
subprocess.run(['git', 'push', 'origin', 'master'], cwd=ROOT, check=True)
print('✅ committed and pushed:', msg)
