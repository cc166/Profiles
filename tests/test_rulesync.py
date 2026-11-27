#!/usr/bin/env python3
"""Regression tests for the upstream rule sync.

Run from the repository root:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'upstream' / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import sync_upstream_rules as sync  # noqa: E402


class ConversionTest(unittest.TestCase):
    def convert(self, text: str) -> tuple[str, dict]:
        return sync.convert_loon_to_core(text + '\n')

    def test_inline_slash_comment_keeps_no_resolve(self):
        out, dropped = self.convert('IP-CIDR,10.0.0.0/8,no-resolve // lan')
        self.assertEqual(out, 'payload:\n  - IP-CIDR,10.0.0.0/8,no-resolve  # lan\n')
        self.assertEqual(dropped, {})

    def test_inline_hash_comment_only_after_whitespace(self):
        out, _ = self.convert('DOMAIN-SUFFIX,foo.com#frag')
        self.assertIn('DOMAIN-SUFFIX,foo.com#frag', out)

    def test_regex_value_with_commas_is_not_truncated(self):
        out, _ = self.convert(r'DOMAIN-REGEX,^cdn[0-9]{2,3}\.example\.com$')
        self.assertIn(r'DOMAIN-REGEX,^cdn[0-9]{2,3}\.example\.com$', out)

    def test_whole_line_slash_comment_becomes_yaml_comment(self):
        out, _ = self.convert('// note\nDOMAIN,example.com')
        self.assertEqual(out, 'payload:\n# note\n  - DOMAIN,example.com\n')

    def test_logic_spacing_normalized(self):
        out, _ = self.convert('AND, ((GEOIP, CN), (DOMAIN, pitaya.bytedance.com))')
        self.assertEqual(out, 'payload:\n  - AND,((GEOIP,CN),(DOMAIN,pitaya.bytedance.com))\n')

    def test_nested_not_preserved(self):
        out, _ = self.convert('AND,((NOT,((DOMAIN-SUFFIX,a.com))),(DOMAIN-KEYWORD,b))')
        self.assertIn('AND,((NOT,((DOMAIN-SUFFIX,a.com))),(DOMAIN-KEYWORD,b))', out)

    def test_unsupported_nested_matcher_drops_whole_rule(self):
        out, dropped = self.convert('AND,((DOMAIN-KEYWORD,x),(PROTOCOL,TCP))')
        self.assertEqual(out, '')
        self.assertIn('PROTOCOL', dropped)

    def test_match_is_not_a_provider_rule(self):
        out, dropped = self.convert('MATCH,DIRECT')
        self.assertEqual(out, '')
        self.assertIn('MATCH', dropped)

    def test_malformed_logic_is_dropped(self):
        out, dropped = self.convert('AND,((DOMAIN-KEYWORD,x)')
        self.assertEqual(out, '')
        self.assertIn('AND(malformed)', dropped)

    def test_duplicate_rules_are_counted(self):
        out, dropped = self.convert('DOMAIN,a.com\nDOMAIN,a.com')
        self.assertEqual(out.count('- DOMAIN,a.com'), 1)
        self.assertEqual(dropped.get('(duplicate)'), 1)


class PublishedFilesTest(unittest.TestCase):
    """The committed products must stay reproducible from their sources."""

    def test_derived_core_matches_committed_files(self):
        for core_name, loon_name in sync.CORE_FROM_LOON.items():
            with self.subTest(core=core_name):
                source = (sync.LOON_DIR / f'{loon_name}.lsr').read_text(encoding='utf-8')
                published = (sync.CORE_DIR / f'{core_name}.yaml').read_text(encoding='utf-8')
                converted, _ = sync.convert_loon_to_core(source)
                self.assertEqual(converted, published)

    def test_sanitize_is_idempotent_on_committed_core(self):
        files = sorted(sync.CORE_DIR.glob('*.yaml'))
        self.assertTrue(files)
        for path in files:
            with self.subTest(file=path.name):
                text = path.read_text(encoding='utf-8')
                sanitized, _ = sync.sanitize_core_text(text)
                self.assertEqual(sanitized, text)

    def test_check_existing_passes(self):
        self.assertEqual(sync.check_existing(), 0)


class FallbackScopeTest(unittest.TestCase):
    """Only upstream failures may fall back; local errors must abort."""

    def _run_sync_group(self, side_effect):
        original = sync.fetch_validated
        sync.fetch_validated = side_effect
        try:
            with tempfile.TemporaryDirectory() as tmp:
                stage = Path(tmp)
                return sync.sync_group(
                    'loon_remote', {'AI': 'https://example.invalid/AI.lsr'},
                    sync.LOON_DIR, '.lsr', 'ua', 'Accept: */*',
                    sync.looks_like_loon_rules, stage,
                )
        finally:
            sync.fetch_validated = original

    def test_fetch_error_falls_back_to_committed_file(self):
        def boom(*_args, **_kwargs):
            raise sync.FetchError('upstream down')

        section = self._run_sync_group(boom)
        self.assertEqual(section['kept'], ['AI'])
        self.assertEqual(section['ok'], [])

    def test_local_error_is_not_swallowed(self):
        def boom(*_args, **_kwargs):
            raise OSError('disk full')

        with self.assertRaises(OSError):
            self._run_sync_group(boom)


if __name__ == '__main__':
    unittest.main()
