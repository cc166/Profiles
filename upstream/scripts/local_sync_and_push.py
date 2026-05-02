#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / 'upstream' / 'scripts' / 'sync_upstream_rules.py'
REPORT = ROOT / 'upstream' / '_sync_report.json'


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


# Keep paired custom rule files in sync before mirroring upstream rules.
run(['python3', 'sync_rules.py', '--from', 'lsr'])
run(['python3', 'validate_custom_rules.py'])

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

run(['git', 'add', 'custom-rules', 'upstream'])
diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT)
if diff.returncode == 0:
    print('✅ rules already up to date; nothing to push')
    raise SystemExit(0)

run(['git', 'config', '--local', 'user.email', 'minis-local-sync@users.noreply.github.com'])
run(['git', 'config', '--local', 'user.name', 'minis-local-sync'])
msg = f'chore: sync rules (local) core {core_ok}/{expected_core}, loon {loon_ok}/{expected_loon}'
run(['git', 'commit', '-m', msg])
push_cmd = ['git', 'push', 'origin', 'master']
token = os.environ.get('GITHUB_TOKEN_5')
if token:
    auth = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
    push_cmd = ['git', '-c', f'http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}', 'push', 'origin', 'master']
run(push_cmd)
print('✅ committed and pushed:', msg)
