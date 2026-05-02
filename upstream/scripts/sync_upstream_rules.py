#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).parent))
from config import CLASH_RULES, UA_CLASH, UA_LOON  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = ROOT / 'upstream' / 'core'
LOON_DIR = ROOT / 'upstream' / 'loon'
REPORT_PATH = ROOT / 'upstream' / '_sync_report.json'
FAILED_REPORT_PATH = ROOT / 'upstream' / '_sync_report.failed.json'

LOON_REMOTE_SOURCES = {
    'LAN_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/LAN_SPLITTER.lsr',
    'REGION_SPLITTER': 'https://kelee.one/Tool/Loon/Lsr/REGION_SPLITTER.lsr',
    'AI': 'https://kelee.one/Tool/Loon/Lsr/AI.lsr',
    'OpenAI': 'https://rule.kelee.one/Loon/OpenAI.lsr',
    'Claude': 'https://rule.kelee.one/Loon/Claude.lsr',
    'Gemini': 'https://rule.kelee.one/Loon/Gemini.lsr',
    'Anthropic': 'https://rule.kelee.one/Loon/Anthropic.lsr',
    'Copilot': 'https://rule.kelee.one/Loon/Copilot.lsr',
    'Netflix': 'https://rule.kelee.one/Loon/Netflix.lsr',
    'Disney': 'https://rule.kelee.one/Loon/Disney.lsr',
    'YouTube': 'https://rule.kelee.one/Loon/YouTube.lsr',
    'Spotify': 'https://rule.kelee.one/Loon/Spotify.lsr',
    'HBO': 'https://rule.kelee.one/Loon/HBO.lsr',
    'PrimeVideo': 'https://rule.kelee.one/Loon/PrimeVideo.lsr',
    'DiscoveryPlus': 'https://rule.kelee.one/Loon/DiscoveryPlus.lsr',
    'Bahamut': 'https://rule.kelee.one/Loon/Bahamut.lsr',
    'Emby': 'https://rule.kelee.one/Loon/Emby.lsr',
    'Telegram': 'https://rule.kelee.one/Loon/Telegram.lsr',
    'Twitter': 'https://rule.kelee.one/Loon/Twitter.lsr',
    'Facebook': 'https://rule.kelee.one/Loon/Facebook.lsr',
    'Instagram': 'https://rule.kelee.one/Loon/Instagram.lsr',
    'Apple': 'https://rule.kelee.one/Loon/Apple.lsr',
    'AppleAccount': 'https://kelee.one/Tool/Loon/Lsr/AppleAccount.lsr',
    'AppStore': 'https://kelee.one/Tool/Loon/Lsr/AppStore.lsr',
    'AppleTV': 'https://rule.kelee.one/Loon/AppleTV.lsr',
    'Google': 'https://rule.kelee.one/Loon/Google.lsr',
    'GoogleFCM': 'https://rule.kelee.one/Loon/GoogleFCM.lsr',
    'OneDrive': 'https://rule.kelee.one/Loon/OneDrive.lsr',
    'Microsoft': 'https://rule.kelee.one/Loon/Microsoft.lsr',
    'GitHub': 'https://rule.kelee.one/Loon/GitHub.lsr',
    'TikTok': 'https://kelee.one/Tool/Loon/Lsr/TikTok.lsr',
    'Game': 'https://rule.kelee.one/Loon/Game.lsr',
    'Speedtest': 'https://rule.kelee.one/Loon/Speedtest.lsr',
    'SpeedtestInternational': 'https://kelee.one/Tool/Loon/Lsr/SpeedtestInternational.lsr',
    'ChinaDownloadCDN': 'https://kelee.one/Tool/Loon/Lsr/ChinaDownloadCDN.lsr',
    'InternationalDownloadCDN': 'https://kelee.one/Tool/Loon/Lsr/InternationalDownloadCDN.lsr',
    'Steam': 'https://rule.kelee.one/Loon/Steam.lsr',
    'ReelShort': 'https://kelee.one/Tool/Loon/Lsr/ReelShort.lsr',
    'Proxy': 'https://kelee.one/Tool/Loon/Lsr/Proxy.lsr',
    'Direct': 'https://kelee.one/Tool/Loon/Lsr/Direct.lsr',
}

UA_POOL_CLASH = ['clash.meta', 'clash.meta/1.18.10', 'mihomo/1.18.10', 'ClashforWindows/0.20.39']
UA_POOL_LOON = [UA_LOON, 'Loon/840 CFNetwork/1494.0.7 Darwin/23.4.0', 'Loon/838 CFNetwork/1490.0.4 Darwin/23.2.0']
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'


def snippet(text: str, limit: int = 220) -> str:
    return re.sub(r'\s+', ' ', text[:limit]).strip()


def accept_value(accept_header: str) -> str:
    return accept_header.split(':', 1)[1].strip() if ':' in accept_header else accept_header


def browser_headers(url: str, ua: str, accept_header: str) -> dict[str, str]:
    origin = 'https://rule.kelee.one/' if 'rule.kelee.one' in url else 'https://kelee.one/'
    return {
        'User-Agent': ua,
        'Accept': accept_value(accept_header),
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': origin,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }


def curl_once(url: str, ua: str, accept_header: str, http1: bool) -> tuple[str, str]:
    cmd = ['curl']
    if http1:
        cmd.append('--http1.1')
    cmd += [
        '-L', '-k', '--compressed', '--connect-timeout', '8', '--max-time', '20',
        '-A', ua,
    ]
    for key, value in browser_headers(url, ua, accept_header).items():
        if key != 'User-Agent':
            cmd += ['-H', f'{key}: {value}']
    cmd += ['-sS', '-w', '\n__CURL_META__%{http_code}|%{content_type}|%{url_effective}', url]
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    stdout = r.stdout or ''
    body, meta = stdout, f'curl rc={r.returncode}'
    if '\n__CURL_META__' in stdout:
        body, raw_meta = stdout.rsplit('\n__CURL_META__', 1)
        meta = f'curl rc={r.returncode} meta={raw_meta.strip()}'
    if r.stderr.strip():
        meta += f' stderr={snippet(r.stderr)}'
    return body, meta


def curl_cffi_once(url: str, ua: str, accept_header: str) -> tuple[str, str]:
    from curl_cffi import requests  # type: ignore

    headers = browser_headers(url, ua, accept_header)
    headers['User-Agent'] = BROWSER_UA
    r = requests.get(url, headers=headers, timeout=20, impersonate='chrome120')
    return r.text, f'curl_cffi status={r.status_code} ctype={r.headers.get("content-type", "")}'


def fetch_validated(url: str, ua: str, accept_header: str, validator: Callable[[str], bool], kind: str) -> tuple[str, str]:
    errors: list[str] = []
    ua_pool = UA_POOL_CLASH if kind == 'core' else UA_POOL_LOON
    strategies: list[tuple[str, Callable[[], tuple[str, str]]]] = []

    # GitHub-hosted runners are currently blocked by upstream CDN. Keep the
    # protected last-good report and fail fast instead of spending minutes on
    # doomed browser/TLS impersonation retries.
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        raise RuntimeError('CI/remote runner is blocked by upstream CDN/Cloudflare; run from the self-hosted sync VM or another allowed network')

    # curl_cffi changes the TLS/JA3 fingerprint; normal curl only changes HTTP headers.
    try:
        import curl_cffi  # noqa: F401
        strategies.append(('curl_cffi/chrome120', lambda: curl_cffi_once(url, BROWSER_UA, accept_header)))
    except Exception as exc:
        errors.append(f'curl_cffi unavailable: {exc.__class__.__name__}')

    for idx in range(2):
        current_ua = ua if idx == 0 else random.choice(ua_pool)
        strategies.append((f'curl-http1.1/{current_ua}', lambda u=current_ua: curl_once(url, u, accept_header, True)))
    current_ua = random.choice(ua_pool)
    strategies.append((f'curl-default/{current_ua}', lambda u=current_ua: curl_once(url, u, accept_header, False)))

    for idx, (method, fn) in enumerate(strategies, 1):
        if idx > 1:
            time.sleep(min(3, idx * 0.5) + random.uniform(0, 0.5))
        try:
            text, meta = fn()
        except Exception as exc:
            errors.append(f'{method}: {exc.__class__.__name__}: {exc}')
            continue
        if text.strip() and validator(text):
            return text, method
        errors.append(f'{method}: invalid ({meta}) head={snippet(text)}')
    raise RuntimeError(' || '.join(errors[-6:]))


def looks_like_payload(text: str) -> bool:
    head = text[:800].lower()
    if any(x in head for x in ('<!doctype html', '<html', 'just a moment', 'cf-chl', 'forbidden', 'access denied')):
        return False
    return any(line.strip() == 'payload:' for line in text.splitlines()[:40])


def looks_like_loon_rules(text: str) -> bool:
    head = text[:800].lower()
    if any(x in head for x in ('<!doctype html', '<html', 'just a moment', 'cf-chl', 'forbidden', 'access denied')):
        return False
    return any(',' in s for s in (line.strip() for line in text.splitlines()) if s and not s.startswith(('#', '//', ';')))


def existing_ok(path: Path, kind: str) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return False
    return looks_like_payload(text) if kind == 'core' else looks_like_loon_rules(text)


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def sort_section(section: dict) -> dict:
    # Keep insertion order stable with config order; this avoids noisy report diffs.
    return section


def sync_group(name: str, items: dict[str, str], out_dir: Path, suffix: str, ua: str, accept_header: str, validator: Callable[[str], bool]) -> dict:
    section = {'ok': [], 'failed': [], 'kept': [], 'source': {}, 'status': {}}
    for rule_name, url in items.items():
        rel = f'{out_dir.relative_to(ROOT)}/{rule_name}{suffix}'
        path = out_dir / f'{rule_name}{suffix}'
        try:
            text, method = fetch_validated(url, ua, accept_header, validator, name)
            save_text(path, text)
            section['ok'].append(rule_name)
            section['source'][rule_name] = {'url': url, 'method': method, 'ua': ua}
            section['status'][rule_name] = 'updated-verified'
        except Exception as exc:
            kept = existing_ok(path, name)
            if kept:
                section['kept'].append(rule_name)
                section['source'][rule_name] = {'url': url, 'method': 'last-known-good', 'ua': ua, 'note': 'latest fetch failed; kept existing verified file'}
                section['status'][rule_name] = 'kept-last-known-good'
            else:
                section['status'][rule_name] = 'failed-verified'
            section['failed'].append({'name': rule_name, 'path': rel, 'url': url, 'error': str(exc), 'kept_last_good': kept})
    return sort_section(section)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    report = {
        'meta': {
            'note': 'ok=downloaded this run; failed+kept_last_good=true means latest fetch failed but existing verified file was preserved',
            'expected_core': len(CLASH_RULES),
            'expected_loon': len(LOON_REMOTE_SOURCES),
            'schedule_hint': 'self-hosted systemd timer; run upstream/scripts/local_sync_and_push.py',
        }
    }
    report['core'] = sync_group('core', CLASH_RULES, CORE_DIR, '.yaml', UA_CLASH, 'Accept: application/yaml,text/yaml,*/*;q=0.9', looks_like_payload)
    report['loon_remote'] = sync_group('loon_remote', LOON_REMOTE_SOURCES, LOON_DIR, '.lsr', UA_LOON, 'Accept: text/plain,*/*;q=0.9', looks_like_loon_rules)
    summary = {
        'core_ok': len(report['core']['ok']),
        'core_failed': len(report['core']['failed']),
        'core_kept': len(report['core']['kept']),
        'loon_ok': len(report['loon_remote']['ok']),
        'loon_failed': len(report['loon_remote']['failed']),
        'loon_kept': len(report['loon_remote']['kept']),
    }
    print(json.dumps(summary, ensure_ascii=False))

    failed_count = summary['core_failed'] + summary['loon_failed']
    allow_kept = os.environ.get('ALLOW_KEPT_ON_FAIL') == '1'
    if failed_count and not allow_kept:
        write_json(FAILED_REPORT_PATH, report)
        print(f'upstream fetch incomplete; kept tracked {REPORT_PATH} unchanged; diagnostics: {FAILED_REPORT_PATH}', file=sys.stderr)
        return 1

    write_json(REPORT_PATH, report)
    if FAILED_REPORT_PATH.exists():
        FAILED_REPORT_PATH.unlink()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
