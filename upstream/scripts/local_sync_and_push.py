#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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
push_cmd = ['git', 'push', 'origin', 'master']
token = os.environ.get('GITHUB_TOKEN_5')
if token:
    import base64
    auth = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
    push_cmd = ['git', '-c', f'http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}', 'push', 'origin', 'master']
subprocess.run(push_cmd, cwd=ROOT, check=True)
print('✅ committed and pushed:', msg)
