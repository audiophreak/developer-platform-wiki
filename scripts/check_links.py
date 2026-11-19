#!/usr/bin/env python3
"""Validate the manual's structure: navigation targets, internal links and anchors, and Mermaid diagrams.

Checks, all failing the run:

- every `nav` entry in zensical.toml names an existing page, and every page is in `nav`;
- every relative Markdown link resolves to an existing file, and its `#anchor` (if any) to a heading on that page;
- every same-page `#anchor` link resolves;
- after a build (`site/` present), the number of `class="mermaid"` placeholders equals the number of Mermaid blocks.
"""

from __future__ import annotations

import re
import sys
import tomllib
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^(```|~~~)")
MERMAID = re.compile(r"^```mermaid\s*$", re.MULTILINE)


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


def slugify(text: str) -> str:
    """Python-Markdown's toc slugify: strip markup, NFKD to ASCII, drop punctuation, hyphenate whitespace."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def prose_lines(body: str) -> list[str]:
    """Lines outside fenced code blocks."""
    lines, fenced = [], False
    for line in body.splitlines():
        if FENCE.match(line.lstrip()):
            fenced = not fenced
            continue
        if not fenced:
            lines.append(line)
    return lines


def anchors_of(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    for line in prose_lines(path.read_text()):
        match = HEADING.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        found.add(slug if n == 0 else f"{slug}_{n}")
    return found


def main() -> int:
    config = tomllib.loads((ROOT / "zensical.toml").read_text())
    nav = nav_files(config["project"]["nav"])
    errors: list[str] = []

    for rel in nav:
        if not (DOCS / rel).is_file():
            errors.append(f"navigation target missing: docs/{rel}")
    pages = sorted(p.relative_to(DOCS).as_posix() for p in DOCS.rglob("*.md"))
    for rel in pages:
        if rel not in nav:
            errors.append(f"page not in navigation: docs/{rel}")

    anchor_cache: dict[Path, set[str]] = {}
    links = 0
    for source in sorted(DOCS.rglob("*.md")):
        text = "\n".join(prose_lines(source.read_text()))
        text = re.sub(r"`[^`\n]*`", "", text)  # inline code is not a link
        for match in LINK.finditer(text):
            raw = match.group(1).strip("<>")
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc:
                continue
            links += 1
            target = (source.parent / unquote(parts.path)).resolve() if parts.path else source
            where = source.relative_to(ROOT)
            if not target.is_file():
                errors.append(f"{where}: link target missing: {raw}")
                continue
            if parts.fragment:
                anchors = anchor_cache.setdefault(target, anchors_of(target))
                if parts.fragment not in anchors:
                    errors.append(f"{where}: anchor not found: {raw}")

    diagrams = sum(len(MERMAID.findall(p.read_text())) for p in DOCS.rglob("*.md"))
    site = ROOT / "site"
    placeholders = (
        sum(p.read_text(errors="replace").count('class="mermaid"') for p in site.rglob("*.html"))
        if site.is_dir()
        else None
    )
    if placeholders is not None and placeholders != diagrams:
        errors.append(f"Mermaid build mismatch: {diagrams} source blocks, {placeholders} rendered placeholders")

    if errors:
        print("Documentation structure check FAILED:")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    built = f", {placeholders} placeholders in the build" if placeholders is not None else " (no build to compare)"
    print(f"OK: {len(nav)} navigation entries, {len(pages)} pages, {links} internal links and anchors resolve; "
          f"{diagrams} Mermaid diagrams{built}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
