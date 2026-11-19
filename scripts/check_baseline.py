#!/usr/bin/env python3
"""Fail if a high-authority "current baseline" location disagrees with baseline.toml.

baseline.toml is the single definition of the current accepted baseline (versions, commits, tag objects). This check
looks only at the locations that claim to describe *the current* baseline: the site footer, the README and home-page
tables, the release and source-map tables, and the generated-project examples in Getting Started and the command
reference. Everywhere else (history, the source map's historical sections, evidence, "since 0.x" feature facts) older
releases are legitimate, so old version strings are not banned globally.

Each rule names a file and a pattern with one capture group: every match must equal the current value, and a
`required` rule must match at least once. A rule that matches nothing fails too, so a rewritten page cannot silently
drop out of the check.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = r"(?: \(`[0-9a-f]{7,40}`\))?"  # an optional short commit after a version in a table cell
REPO = {"platform": "developer-platform", "web": "web-core-template", "native": "native-ios-template"}


def rules(b: dict[str, dict[str, str]]) -> list[tuple[str, str, str]]:
    """(file, regex with one group, expected value)."""
    v = {k: b[k]["version"] for k in REPO}
    c = {k: b[k]["commit"] for k in REPO}
    r: list[tuple[str, str, str]] = []
    for key, repo in REPO.items():
        r += [
            ("zensical.toml", rf"{repo} (v\d+\.\d+\.\d+)", v[key]),
            ("README.md", rf"\| `audiophreak/{repo}` \| `(v[\d.]+)` \|", v[key]),
            ("README.md", rf"\| `audiophreak/{repo}` \| `v[\d.]+` \| `([0-9a-f]{{40}})` \|", c[key]),
            ("docs/index.md", rf"\| `audiophreak/{repo}` \| `(v[\d.]+)` \|", v[key]),
            ("docs/index.md", rf"\| `audiophreak/{repo}` \| `v[\d.]+` \| `([0-9a-f]{{40}})` \|", c[key]),
            ("docs/releases/index.md", rf"\| `audiophreak/{repo}` \| \*\*`(v[\d.]+)`\*\* \|", v[key]),
            ("docs/releases/index.md", rf"\| `audiophreak/{repo}` \| \*\*`v[\d.]+`\*\* \| `([0-9a-f]{{40}})` \|", c[key]),
            ("docs/reference/source-map.md", rf"\| {repo} \| \*\*`(v[\d.]+)`\*\* \(current\) \|", v[key]),
            ("docs/reference/source-map.md", rf"\| {repo} \| \*\*`v[\d.]+`\*\* \(current\) \| `[0-9a-f]{{40}}` \| `([0-9a-f]{{40}})` \|", c[key]),
            ("docs/reference/source-map.md", rf"\| {repo} \| \*\*`v[\d.]+`\*\* \(current\) \| `([0-9a-f]{{40}})` \|", b[key]["tag_object"]),
        ]
    r += [
        # the current-baseline row of the release page's history table
        ("docs/releases/index.md", rf"\| \*\*Current\*\* \([^)]*\) \| `(v[\d.]+)`{SHA} \|", v["platform"]),
        ("docs/releases/index.md", rf"\| \*\*Current\*\* \([^)]*\) \| `v[\d.]+`{SHA} \| `(v[\d.]+)`{SHA} \|", v["web"]),
        ("docs/releases/index.md", rf"\| \*\*Current\*\* \([^)]*\) \| `v[\d.]+`{SHA} \| `v[\d.]+`{SHA} \| \*\*`(v[\d.]+)`\*\*", v["native"]),
        # what devkit prints and records for a new project
        ("docs/getting-started/setup.md", r"devkit --version\s+# devkit (\d+\.\d+\.\d+)", v["platform"][1:]),
        ("docs/getting-started/setup.md", r"git checkout (v[\d.]+)\s+# optional: pin", v["platform"]),
        ("docs/commands/devkit.md", r"devkit --version\s+# devkit (\d+\.\d+\.\d+)", v["platform"][1:]),
        ("docs/getting-started/first-web-project.md", r"web-core-template\.git @ (v[\d.]+)", v["web"]),
        ("docs/getting-started/first-web-project.md", r"_commit: (v[\d.]+)", v["web"]),
        ("docs/getting-started/native-ios-project.md", r"native-ios-template\.git @ (v[\d.]+)", v["native"]),
        ("docs/getting-started/native-ios-project.md", r"\bweb\s+(v[\d.]+)\s+up to date", v["web"]),
        ("docs/getting-started/native-ios-project.md", r"\bnative\s+(v[\d.]+)\s+up to date", v["native"]),
        ("docs/getting-started/native-ios-project.md", r"\(web `(v[\d.]+)`, native `v[\d.]+`\)", v["web"]),
        ("docs/getting-started/native-ios-project.md", r"\(web `v[\d.]+`, native `(v[\d.]+)`\)", v["native"]),
        ("docs/getting-started/native-ios-project.md", r"`\.copier-answers\.ios\.yml` \(native, records `_src_path`, `_commit: (v[\d.]+)`", v["native"]),
        ("docs/architecture/generated-projects.md", r"_commit: (v[\d.]+)\n_src_path: https://github\.com/audiophreak/web-core-template", v["web"]),
        ("docs/architecture/generated-projects.md", r"_commit: (v[\d.]+)\n_src_path: https://github\.com/audiophreak/native-ios-template", v["native"]),
        ("docs/commands/devkit.md", r"\bweb\s+(v[\d.]+)\s+up to date", v["web"]),
        ("docs/commands/devkit.md", r"\bnative\s+(v[\d.]+)\s+up to date", v["native"]),
    ]
    return r


def main() -> int:
    baseline = tomllib.loads((ROOT / "baseline.toml").read_text())["current"]
    errors: list[str] = []
    checked = 0
    for rel, pattern, expected in rules(baseline):
        text = (ROOT / rel).read_text()
        found = re.findall(pattern, text)
        if not found:
            errors.append(f"{rel}: no current-baseline match for /{pattern}/ (expected {expected})")
        for value in found:
            checked += 1
            if value != expected:
                errors.append(f"{rel}: found {value}, the current baseline is {expected} (/{pattern}/)")
    if errors:
        print("Current-baseline check FAILED (baseline.toml is the source of truth):")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    names = ", ".join(f"{REPO[k]} {baseline[k]['version']}" for k in REPO)
    print(f"OK: {checked} current-baseline references agree with baseline.toml ({names}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
