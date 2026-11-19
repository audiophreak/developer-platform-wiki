#!/usr/bin/env python3
"""Fail if the manual contains secrets, credentials, personal data or machine paths, or inconsistent baseline SHAs.

Scans every tracked text file of the source (docs/, scripts/, configuration, README). Matches are reported by
file and line with the matching text masked, so the check never prints a secret it finds.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED = [ROOT / "docs", ROOT / "scripts", ROOT / "README.md", ROOT / "zensical.toml", ROOT / "pyproject.toml",
           ROOT / ".github"]

# The accepted baseline: every full 40-hex SHA that names one of these releases must be the right one.
EXPECTED_SHAS = {
    "developer-platform": "e185d6d2c4ac9edde5db7963458c8146e4c229d2",
    "web-core-template": "094e35b8b32d6186d609695f940afeb91a9b5990",
    "native-ios-template": "f0f4a5a8ac58825e94a38068df1bdd413d2f1596",  # v0.1.1
}
# Other full SHAs that may legitimately appear (annotated tag objects, pinned actions, a contract checksum prefix).
ALLOWED_SHAS = {
    "13d9dd6b81954fcd4439f8147630449deb983f50",  # tag object developer-platform v0.8.0
    "90e09368844de6c1f81f3d87547980bcbf442289",  # tag object web-core-template v0.7.0
    "97a3a7ce531b93e01507a8d88da0f88de79d2372",  # tag object native-ios-template v0.1.0 (original accepted release)
    "cd346a01223f82e629649a71fc4d312e4e5c7746",  # commit native-ios-template v0.1.0 (release history)
    "8591c9cd48b829563c74b4cdccec1ce14082e2d5",  # tag object native-ios-template v0.1.1
    "3d3c42e5aac5ba805825da76410c181273ba90b1",  # actions/checkout v7.0.1
    "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",  # actions/setup-python v7.1.0
}

FORBIDDEN = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Stripe-style live key", re.compile(r"sk_live_[A-Za-z0-9]{10,}")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.")),
    ("URL with credentials", re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@'\"]+:(?!postgres@)[^@\s'\"<…]{6,}@")),
    ("home directory path", re.compile(r"/Users/[A-Za-z0-9._-]+|/home/[a-z][a-z0-9._-]+")),
    ("macOS temporary path", re.compile(r"/private/(?:tmp|var)/|/var/folders/")),
    ("personal email", re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|icloud|me|outlook|hotmail|yahoo)\.com", re.I)),
    ("simulator or device UDID", re.compile(r"\b[0-9A-F]{8}-(?:[0-9A-F]{4}-){3}[0-9A-F]{12}\b")),
]

SHA = re.compile(r"\b[0-9a-f]{40}\b")


def files() -> list[Path]:
    found: list[Path] = []
    for entry in SCANNED:
        if entry.is_file():
            found.append(entry)
        elif entry.is_dir():
            found.extend(p for p in entry.rglob("*") if p.is_file() and p.suffix in {".md", ".py", ".toml", ".yml", ".yaml"})
    return sorted(found)


def main() -> int:
    errors: list[str] = []
    this = Path(__file__).resolve()
    for path in files():
        rel = path.relative_to(ROOT)
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if path.resolve() != this:
                for label, pattern in FORBIDDEN:
                    if pattern.search(line):
                        errors.append(f"{rel}:{number}: {label}")
            for sha in SHA.findall(line):
                if sha in EXPECTED_SHAS.values() or sha in ALLOWED_SHAS:
                    continue
                errors.append(f"{rel}:{number}: unexpected full SHA {sha[:12]}… (not the baseline or an allowed pin)")
            for repo, expected in EXPECTED_SHAS.items():
                for sha in SHA.findall(line):
                    if repo in line and sha in EXPECTED_SHAS.values() and sha != expected and line.count("|") < 3:
                        errors.append(f"{rel}:{number}: {repo} paired with another release's SHA")

    if errors:
        print("Content check FAILED:")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"OK: {len(files())} files scanned; no secrets, credentials, personal data or machine paths; "
          "baseline SHAs consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
