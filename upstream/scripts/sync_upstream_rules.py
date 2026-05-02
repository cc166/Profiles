#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import CLASH_RULES, UA_CLASH, UA_LOON  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = ROOT / 'upstream' / 'core'
LOON_DIR = ROOT / 'upstream' / 'loon'
REPORT_PATH = ROOT / 'upstream' / '_sync_report.json'

# Keep this list in one place; it mirrors every file we publish under upstream/loon.
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

UA_POOL_CLASH = ['clash.meta', 'clash.meta/1.18.10', 'mihomo/1.18.10']
UA_POOL_LOON = [UA_LOON, 'Loon/840 CFNetwork/1494.0.7 Darwin/23.4.0']


def curl_fetch(url: str, ua: str, accept: str, tries: int = 4) -> str:
    errors: list[str] = []
    for idx in range(tries):
        if idx:
            time.sleep(min(20, 2 ** idx) + random.uniform(0, 1.5))
        current_ua = ua if idx == 0 else random.choice(UA_POOL_CLASH if 'yaml' in accept else UA_POOL_LOON)
        cmd = [
            'curl', '--http1.1', '-L', '-k', '--compressed',
            '--retry', '2', '--retry-all-errors', '--retry-delay', '2',
            '--connect-timeout', '20', '--max-time', '90',
            '-A', current_ua,
            '-H', accept,
            '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
            '-H', 'Cache-Control: no-cache',
            '-sS', url,
        ]
        r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
        errors.append(r.stderr.strip() or f'curl exit {r.returncode}')
    raise RuntimeError(' | '.join(errors[-3:]) or 'empty response')


def looks_like_payload(text: str) -> bool:
    head = text[:600].lower()
    if any(x in head for x in ('<!doctype html', '<html', 'just a moment', 'cf-chl', 'forbidden')):
        return False
    return any(line.strip() == 'payload:' for line in text.splitlines()[:30])


def looks_like_loon_rules(text: str) -> bool:
    head = text[:600].lower()
    if any(x in head for x in ('<!doctype html', '<html', 'just a moment', 'cf-chl', 'forbidden')):
        return False
    count = 0
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith(('#', '//', ';')):
            continue
        if ',' in s:
            count += 1
            if count >= 1:
                return True
    return False


def existing_ok(path: Path, kind: str) -> bool:
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return False
    return looks_like_payload(text) if kind == 'core' else looks_like_loon_rules(text)


def save(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def sync_group(name: str, items: dict[str, str], out_dir: Path, suffix: str, ua: str, accept: str, validator) -> dict:
    section = {'ok': [], 'failed': [], 'kept': [], 'source': {}, 'status': {}}
    pairs = list(items.items())
    random.shuffle(pairs)
    for rule_name, url in pairs:
        rel = f'{out_dir.relative_to(ROOT)}/{rule_name}{suffix}'
        path = out_dir / f'{rule_name}{suffix}'
        try:
            text = curl_fetch(url, ua, accept)
            if not validator(text):
                raise RuntimeError('invalid rule content')
            save(path, text)
            section['ok'].append(rule_name)
            section['source'][rule_name] = {'url': url, 'method': 'curl-http1.1', 'ua': ua}
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
    return section


def main() -> int:
    report = {
        'meta': {
            'note': 'ok=downloaded this run; failed+kept_last_good=true means latest fetch failed but existing verified file was preserved',
            'expected_core': len(CLASH_RULES),
            'expected_loon': len(LOON_REMOTE_SOURCES),
            'schedule_hint': 'sync-upstream-rules.yml cron 23 3 * * * (UTC, daily)',
        }
    }
    report['core'] = sync_group('core', CLASH_RULES, CORE_DIR, '.yaml', UA_CLASH, 'Accept: application/yaml,text/yaml,*/*;q=0.9', looks_like_payload)
    report['loon_remote'] = sync_group('loon_remote', LOON_REMOTE_SOURCES, LOON_DIR, '.lsr', UA_LOON, 'Accept: text/plain,*/*;q=0.9', looks_like_loon_rules)
    save(REPORT_PATH, json.dumps(report, ensure_ascii=False, indent=2))
    summary = {
        'core_ok': len(report['core']['ok']),
        'core_failed': len(report['core']['failed']),
        'core_kept': len(report['core']['kept']),
        'loon_ok': len(report['loon_remote']['ok']),
        'loon_failed': len(report['loon_remote']['failed']),
        'loon_kept': len(report['loon_remote']['kept']),
    }
    print(json.dumps(summary, ensure_ascii=False))
    hard_fail = [x for x in report['core']['failed'] + report['loon_remote']['failed'] if not x.get('kept_last_good')]
    return 1 if hard_fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
