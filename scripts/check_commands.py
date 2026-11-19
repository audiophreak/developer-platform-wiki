#!/usr/bin/env python3
"""Fail if a `devkit` command shown in the manual does not exist in the documented devkit release, or uses an option
that command does not accept.

The command line below is devkit 0.8.x (`devkit COMMAND --help`; identical in 0.8.0 and 0.8.1). The same rule set is
used by native-ios-template's `tests/test_docs_commands.py`; it is repeated here because this repository's CI cannot
read the private template. Update it together with a devkit release that changes the command line.

Only code is checked (fenced blocks and inline code spans, Mermaid excluded), and only where `devkit` stands in
command position: at the start of a span or line, after `uv run [--project DIR]`, `$ `, `gh_git ` or a shell operator.
Prose such as "devkit never overwrites" is not a command.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = {"--help", "-h", "--version"}
OPTIONS: dict[str, set[str]] = {
    "doctor": set(),
    "new": {"--description", "--output-dir", "--profile", "--set", "--template", "--template-ref", "--native-template",
            "--native-template-ref", "--native-set", "--dry-run"},
    "upgrade": {"--to", "--set", "--profile", "--layer", "--dry-run"},
    "status": set(),
    "native add": {"--native-template", "--native-template-ref", "--native-set", "--dry-run"},
}  # fmt: skip
CHOICES = {"--layer": {"auto", "web", "native"}, "--profile": {"web-core", "full-stack", "native-ios"}}
FENCE = re.compile(r"^```(\w*)[^\n]*\n(.*?)^```", re.S | re.M)
SPAN = re.compile(r"`([^`\n]+)`")
POSITION = re.compile(r"(?:^|&&|\|\||;|\$ |gh_git |uv run (?:--locked )?(?:--project \S+ )?)\s*devkit\s+([a-z][a-z-]*)((?:\s+(?!#)[^\s`)|;]+)*)")


def problems(line: str) -> list[str]:
    bad = []
    for match in POSITION.finditer(line.strip()):
        command, args = match.group(1), match.group(2).split()
        if command == "native":
            command = "native " + (args.pop(0) if args else "")
        if command not in OPTIONS:
            bad.append(f"devkit {command}: no such command")
            continue
        for i, arg in enumerate(args):
            if not arg.startswith("-"):
                continue
            name, _, value = arg.partition("=")
            if name not in OPTIONS[command] | GLOBAL:
                bad.append(f"devkit {command}: no option {name}")
            choice = value or (args[i + 1] if i + 1 < len(args) else "")
            if name in CHOICES and re.fullmatch(r"[a-z-]+", choice) and choice not in CHOICES[name]:
                bad.append(f"devkit {command} {name}: {choice} is not a choice")
    return bad


def code_lines(text: str) -> list[str]:
    lines = []
    for lang, body in FENCE.findall(text):
        if lang != "mermaid":
            lines += body.splitlines()
    prose = FENCE.sub("", text)
    lines += SPAN.findall(prose)
    return lines


def main() -> int:
    errors, checked = [], 0
    for path in sorted([*(ROOT / "docs").rglob("*.md"), ROOT / "README.md"]):
        for line in code_lines(path.read_text()):
            checked += len(POSITION.findall(line.strip()))
            errors += [f"{path.relative_to(ROOT)}: {p} :: {line.strip()[:100]}" for p in problems(line)]
    # Negative control: the checker must reject what does not exist, or it proves nothing.
    for wrong in ("devkit upgrade-native", "devkit new app --database postgres", "devkit upgrade . --layer ios", "devkit native remove ."):
        if not problems(wrong):
            errors.append(f"self-test: the checker accepted `{wrong}`")
    if errors:
        print("Command syntax check FAILED:")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"OK: {checked} devkit commands in code are valid for devkit 0.8.x; self-test rejected 4 invalid commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
