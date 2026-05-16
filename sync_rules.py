#!/usr/bin/env python3
"""
Sync paired custom rule files in custom-rules/.

Use case:
- Edit either custom-rules/Foo.lsr (Loon) or custom-rules/Foo.yaml (Clash classical payload).
- When automation supplies git history, the file changed in the triggering commit is the source.
- For stable pairs without source files, DEFAULT_SOURCE_BY_STEM prevents mtime from picking
  the wrong side on a fresh checkout.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parent
CUSTOM_RULES = ROOT / "custom-rules"
DEFAULT_SOURCE_BY_STEM = {
    # Loon is the canonical editable source for this custom direct-rule pair.
    "self-use-loon-rules": "lsr",
}
PRESERVE_COMMENTS_BY_STEM = {
    "self-use-loon-rules": True,
    "Emby": True,
}
TITLE_BY_YAML_NAME = {
    "self-use-openclash-rules.yaml": "# Local Rules For OpenClash",
}
PAIR_ALIASES = [
    (CUSTOM_RULES / "self-use-loon-rules.lsr", CUSTOM_RULES / "self-use-openclash-rules.yaml"),
]
VALID_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "IP-CIDR",
    "IP-CIDR6",
    "IP-ASN",
    "USER-AGENT",
    "URL-REGEX",
    "GEOIP",
    "PROCESS-NAME",
    "DST-PORT",
    "SRC-IP-CIDR",
    "SRC-PORT",
    "RULE-SET",
    "DOMAIN-SET",
}
LOON_POLICY_FIELDS = {
    "DIRECT",
    "PROXY",
    "REJECT",
    "REJECT-DROP",
    "REJECT-NO-DROP",
    "REJECT-TINYGIF",
    "REJECT-IMG",
    "REJECT-DICT",
}


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def git_diff_names(base: str, head: str = "HEAD") -> set[str]:
    diff = run_git(["diff", "--name-only", base, head, "--", "custom-rules"])
    if diff.returncode != 0:
        return set()
    return {x.strip() for x in diff.stdout.splitlines() if x.strip()}


def changed_files_from_git() -> set[Path]:
    """Return custom rule files changed by the triggering event / working tree."""
    candidates: set[str] = set()

    before = os.environ.get("GITHUB_EVENT_BEFORE", "").strip()
    if before and set(before) != {"0"}:
        candidates.update(git_diff_names(before, "HEAD"))

    parent = run_git(["rev-parse", "--verify", "HEAD^1"])
    if parent.returncode == 0:
        candidates.update(git_diff_names("HEAD^1", "HEAD"))

    for args in (["diff", "--name-only", "--", "custom-rules"], ["diff", "--cached", "--name-only", "--", "custom-rules"]):
        diff = run_git(args)
        if diff.returncode == 0:
            candidates.update(x.strip() for x in diff.stdout.splitlines() if x.strip())

    return {ROOT / x for x in candidates if x.endswith((".lsr", ".yaml", ".yml"))}


def split_inline_comment(content: str) -> tuple[str, str]:
    for idx, char in enumerate(content):
        if char == "#" and idx > 0 and content[idx - 1].isspace():
            body = content[:idx].rstrip()
            return body, content[len(body):]
    return content, ""


def split_rule(content: str) -> Optional[tuple[str, str, list[str], str]]:
    body, comment = split_inline_comment(content)
    parts = [p.strip() for p in body.split(",")]
    if len(parts) < 2:
        return None
    rule_type = parts[0].upper()
    if rule_type not in VALID_RULE_TYPES:
        return None
    return rule_type, parts[1], parts[2:], comment


def parse_loon_line(line: str) -> Optional[tuple[str, str, list[str], str]]:
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "//", ";")):
        return None
    return split_rule(stripped)


def parse_clash_line(line: str) -> Optional[tuple[str, str, list[str], str]]:
    stripped = line.strip()
    if not stripped or stripped == "payload:" or stripped.startswith(("#", "//", ";")):
        return None
    if not stripped.startswith("-"):
        return None
    content = stripped[1:].strip().strip('"').strip("'")
    return split_rule(content)


def normalize_value(rule_type: str, value: str) -> str:
    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}:
        return value.lower()
    return value


def format_rule(rule_type: str, value: str, extras: list[str], comment: str = "") -> str:
    parts = [rule_type, normalize_value(rule_type, value)]
    parts.extend(x for x in extras if x)
    return ",".join(parts) + comment


def loon_to_clash(loon_file: Path, clash_file: Path) -> None:
    preserve_comments = PRESERVE_COMMENTS_BY_STEM.get(loon_file.stem, False)
    title_override = TITLE_BY_YAML_NAME.get(clash_file.name)
    lines = ["payload:"]
    title_written = False
    for raw in loon_file.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped:
            if preserve_comments and not (len(lines) == 1 and lines[0] == "payload:"):
                lines.append("")
            continue
        if stripped.startswith(("#", "//", ";")):
            if preserve_comments:
                if title_override and not title_written and stripped.lower().startswith("# self use rules"):
                    lines.append(title_override)
                    title_written = True
                elif title_override and stripped.lower().startswith("# generated from"):
                    continue
                else:
                    lines.append(raw)
            continue
        parsed = parse_loon_line(raw)
        if parsed:
            rule_type, value, extras, comment = parsed
            extras = [x for x in extras if x.upper() not in LOON_POLICY_FIELDS]
            lines.append(f"  - {format_rule(rule_type, value, extras, comment)}")
    clash_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clash_to_loon(clash_file: Path, loon_file: Path) -> None:
    preserve_comments = PRESERVE_COMMENTS_BY_STEM.get(loon_file.stem, False)
    lines: list[str] = []
    for raw in clash_file.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped == "payload:":
            continue
        if not stripped:
            if preserve_comments:
                lines.append("")
            continue
        if stripped.startswith(("#", "//", ";")):
            if preserve_comments:
                lines.append(raw)
            continue
        parsed = parse_clash_line(raw)
        if parsed:
            rule_type, value, extras, comment = parsed
            policy = [x for x in extras if x.upper() in LOON_POLICY_FIELDS]
            rest = [x for x in extras if x.upper() not in LOON_POLICY_FIELDS]
            if not policy:
                policy = ["DIRECT"]
            lines.append(format_rule(rule_type, value, [*policy, *rest], comment))
    loon_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def choose_source(lsr_file: Path, yaml_file: Path, changed: set[Path]) -> Optional[str]:
    lsr_changed = lsr_file in changed
    yaml_changed = yaml_file in changed
    if lsr_changed and not yaml_changed:
        return "lsr"
    if yaml_changed and not lsr_changed:
        return "yaml"
    if lsr_changed and yaml_changed:
        return "lsr" if lsr_file.stat().st_mtime >= yaml_file.stat().st_mtime else "yaml"

    # Stable pairs may have a preferred source only when Git history / working tree
    # does not identify which side was edited. Do not let the default override an
    # explicit YAML edit; custom-rules must stay bidirectional.
    default_source = DEFAULT_SOURCE_BY_STEM.get(lsr_file.stem)
    if default_source:
        return default_source

    if lsr_file.exists() and yaml_file.exists():
        return "lsr" if lsr_file.stat().st_mtime >= yaml_file.stat().st_mtime else "yaml"
    return None


def paired_files() -> Iterable[tuple[Path, Path]]:
    yielded: set[tuple[Path, Path]] = set()
    for lsr, yaml in PAIR_ALIASES:
        if lsr.exists() and yaml.exists():
            pair = (lsr, yaml)
            yielded.add(pair)
            yield pair

    names = {p.stem for p in CUSTOM_RULES.glob("*.lsr")}
    names.update(p.stem for p in CUSTOM_RULES.glob("*.yaml"))
    for name in sorted(names):
        lsr = CUSTOM_RULES / f"{name}.lsr"
        yaml = CUSTOM_RULES / f"{name}.yaml"
        pair = (lsr, yaml)
        if pair in yielded:
            continue
        if lsr.exists() and yaml.exists():
            default_source = DEFAULT_SOURCE_BY_STEM.get(lsr.stem)
            if default_source:
                yielded.add(pair)
                yield pair


def sync_rules(force: Optional[str] = None) -> list[str]:
    if not CUSTOM_RULES.exists():
        raise FileNotFoundError(f"custom rules directory not found: {CUSTOM_RULES}")

    changed = changed_files_from_git()
    synced: list[str] = []

    for lsr_file, yaml_file in paired_files():
        source = force or choose_source(lsr_file, yaml_file, changed)
        if source == "lsr":
            before = yaml_file.read_text(encoding="utf-8") if yaml_file.exists() else ""
            loon_to_clash(lsr_file, yaml_file)
            if yaml_file.read_text(encoding="utf-8") != before:
                synced.append(f"{lsr_file.relative_to(ROOT)} -> {yaml_file.relative_to(ROOT)}")
        elif source == "yaml":
            before = lsr_file.read_text(encoding="utf-8") if lsr_file.exists() else ""
            clash_to_loon(yaml_file, lsr_file)
            if lsr_file.read_text(encoding="utf-8") != before:
                synced.append(f"{yaml_file.relative_to(ROOT)} -> {lsr_file.relative_to(ROOT)}")

    return synced


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync paired Loon/Clash custom rule files")
    parser.add_argument("--from", dest="force", choices=("lsr", "yaml"), help="force conversion direction")
    args = parser.parse_args()

    synced = sync_rules(args.force)
    if synced:
        print(f"✅ synced {len(synced)} pair(s):")
        for item in synced:
            print(f"  - {item}")
    else:
        print("✅ custom rule pairs already in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
