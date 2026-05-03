#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / 'upstream' / 'scripts' / 'sync_upstream_rules.py'
REPORT = ROOT / 'upstream' / '_sync_report.json'
FAILED_REPORT = ROOT / 'upstream' / '_sync_report.failed.json'
REPORT_ARCHIVE_PATH = Path(os.environ.get('RULESYNC_REPORT_ARCHIVE', str(Path.home() / '.cache' / 'profiles-sync' / 'last_report.json')))
ALLOWED_PREFIXES = ('upstream/core/', 'upstream/loon/', 'upstream/_sync_report.json', 'upstream/_sync_report.failed.json')


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True)


def die(message: str, code: int = 1) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(code)


def changed_outside_allowed() -> list[str]:
    r = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, text=True, capture_output=True, check=True)
    bad: list[str] = []
    for raw in r.stdout.splitlines():
        path = raw[3:] if len(raw) > 3 else raw
        if any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
            continue
        bad.append(raw)
    return bad


def archive_report(report: dict, summary: dict) -> None:
    # Keep diagnostic reports outside the repository. Do not commit report churn to the public repository.
    REPORT_ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    rc = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    head = rc.stdout.strip() if rc.returncode == 0 else 'unknown'
    payload = {'head': head, 'summary': summary, 'report': report}
    REPORT_ARCHIVE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    subprocess.run(['git', 'checkout', '--', 'upstream/_sync_report.json'], cwd=ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if FAILED_REPORT.exists():
        try:
            FAILED_REPORT.unlink()
        except OSError:
            pass


def validate_report() -> tuple[dict, dict]:
    if not REPORT.exists():
        die(f'missing report: {REPORT}')
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    core = report.get('core', {})
    loon = report.get('loon_remote', {})
    meta = report.get('meta', {})
    expected_core = int(meta.get('expected_core', -1))
    expected_loon = int(meta.get('expected_loon', -1))
    core_ok = len(core.get('ok', []))
    core_kept = len(core.get('kept', []))
    loon_ok = len(loon.get('ok', []))
    loon_kept = len(loon.get('kept', []))
    hard_failed = [x for x in core.get('failed', []) + loon.get('failed', []) if not x.get('kept_last_good')]
    if core_ok + core_kept != expected_core:
        die(f'incomplete core sync after fallback: {core_ok}+{core_kept}/{expected_core}')
    if loon_ok + loon_kept != expected_loon:
        die(f'incomplete loon sync after fallback: {loon_ok}+{loon_kept}/{expected_loon}')
    if hard_failed:
        names = ', '.join(str(x.get('name')) for x in hard_failed[:10])
        die(f'no valid fallback for {len(hard_failed)} upstream files: {names}')
    summary = {
        'core_ok': core_ok,
        'core_kept': core_kept,
        'expected_core': expected_core,
        'loon_ok': loon_ok,
        'loon_kept': loon_kept,
        'expected_loon': expected_loon,
    }
    return report, summary


# Boundary: upstream mirror only. Custom-rule automation is intentionally separate.
pre_bad = changed_outside_allowed()
if pre_bad:
    die('working tree has unrelated local changes; refusing upstream sync: ' + '; '.join(pre_bad[:12]))

check_existing = subprocess.run(['python3', str(SYNC), '--check-existing'], cwd=ROOT)
if check_existing.returncode != 0:
    die('existing upstream files failed local validation; manual repair required before network sync')

sync_cmd = ['python3', str(SYNC), '--allow-kept']
r = subprocess.run(sync_cmd, cwd=ROOT)
if r.returncode != 0:
    if FAILED_REPORT.exists():
        print(f'diagnostics written to {FAILED_REPORT}', file=sys.stderr)
    raise SystemExit(r.returncode)

report, summary = validate_report()
archive_report(report, summary)
post_bad = changed_outside_allowed()
if post_bad:
    die('sync touched paths outside upstream mirror boundary: ' + '; '.join(post_bad[:12]))

# Only stage mirrored rule outputs; never stage scripts, reports, or custom rules from this entry point.
run(['git', 'add', 'upstream/core', 'upstream/loon'])
diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT)
if diff.returncode == 0:
    print('✅ upstream rules already up to date; nothing to push')
    raise SystemExit(0)

# Commit only when published files passed the gate. A kept fallback is allowed and visible in the report/message.
run(['git', 'config', '--local', 'user.email', 'minis-local-sync@users.noreply.github.com'])
run(['git', 'config', '--local', 'user.name', 'minis-local-sync'])
msg = (
    'chore: sync upstream rules (local) '
    f"core {summary['core_ok']}+{summary['core_kept']}/{summary['expected_core']}, "
    f"loon {summary['loon_ok']}+{summary['loon_kept']}/{summary['expected_loon']}"
)
run(['git', 'commit', '-m', msg])
push_cmd = ['git', 'push', 'origin', 'master']
token = os.environ.get('GITHUB_TOKEN_5')
if token:
    auth = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
    push_cmd = ['git', '-c', f'http.https://github.com/.extraheader=AUTHORIZATION: basic {auth}', 'push', 'origin', 'master']
run(push_cmd)
print('✅ committed and pushed:', msg)
