#!/usr/bin/env python3
"""Validate local Markdown links and explicit Zensical navigation targets."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
MERMAID = re.compile(r"```mermaid\s*\n", re.IGNORECASE)


def nav_files(items: list[object]) -> list[str]:
    paths: list[str] = []
    for item in items:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    paths.append(value)
                elif isinstance(value, list):
                    paths.extend(nav_files(value))
    return paths


def main() -> int:
    config = tomllib.loads((ROOT / "zensical.toml").read_text())
    errors: list[str] = []
    for rel in nav_files(config["project"]["nav"]):
        if not (DOCS / rel).is_file():
            errors.append(f"navigation target missing: docs/{rel}")

    for source in DOCS.rglob("*.md"):
        body = source.read_text()
        for match in LINK.finditer(body):
            raw = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = (source.parent / unquote(parts.path)).resolve()
            if not target.is_file():
                errors.append(f"{source.relative_to(ROOT)}: local link target missing: {raw}")

    diagram_sources = sum(len(MERMAID.findall(p.read_text())) for p in DOCS.rglob("*.md"))
    built_html = ROOT / "site"
    rendered_slots = sum(p.read_text(errors="replace").count('class="mermaid"') for p in built_html.rglob("*.html")) if built_html.is_dir() else 0
    if diagram_sources < 3:
        errors.append(f"expected at least 3 Mermaid source blocks, found {diagram_sources}")
    if built_html.is_dir() and rendered_slots != diagram_sources:
        errors.append(f"Mermaid build mismatch: {diagram_sources} source blocks, {rendered_slots} rendered placeholders")

    if errors:
        print("Broken local documentation links:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"OK: {len(nav_files(config['project']['nav']))} navigation entries and local Markdown links resolve; {diagram_sources} Mermaid blocks are present in the build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
