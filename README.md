# Developer Platform Manual

The owner, operator and developer manual for the accepted Developer Platform baseline:

| Repository | Release | Commit |
|---|---|---|
| `audiophreak/developer-platform` | `v0.8.1` | `fc464344099bb96b1a58a590c4460e4ead9b1b51` |
| `audiophreak/web-core-template` | `v0.7.1` | `f704572c35147597a24c2b1eb9b99dae332ea05b` |
| `audiophreak/native-ios-template` | `v0.1.1` | `f0f4a5a8ac58825e94a38068df1bdd413d2f1596` |

Published acceptance of the current combination: **192 / 192 gates passed** (native v0.1.1 patch: 177 / 177; original baseline: 151 / 151). The evidence is archived in `docs/evidence/` (see `docs/reference/acceptance-evidence.md`).

Markdown source in `docs/`, built with [Zensical](https://zensical.org/) into a static site for local browsing. Dark theme by default; Mermaid diagrams.

## Browse it (macOS)

Prerequisites: Git, the GitHub CLI (`gh`), [uv](https://docs.astral.sh/uv/), Python 3.11+ (Homebrew `python@3.14` works), and a browser.

```bash
gh repo clone audiophreak/developer-platform-wiki ~/Developer/developer-platform-wiki
cd ~/Developer/developer-platform-wiki
uv sync --locked
uv run zensical serve --open          # http://localhost:8000 ; Ctrl+C to stop
```

To open it in Chrome specifically: `open -a "Google Chrome" http://localhost:8000`.

Diagrams are rendered in the browser by Mermaid, which the theme loads from `unpkg.com`; they need network access while browsing.

## Build and validate

```bash
uv run zensical build --clean --strict     # fails on warnings
uv run python scripts/check_links.py       # navigation, internal links and anchors, Mermaid parity with the build
uv run python scripts/check_content.py     # no secrets, credentials, personal data, machine paths or placeholders
uv run python scripts/check_baseline.py    # current-baseline locations agree with baseline.toml
uv run python scripts/check_commands.py    # devkit commands in examples are valid
python3 -m http.server 8000 --bind 127.0.0.1 --directory site   # browse the built copy without the dev server
```

CI (`.github/workflows/docs.yml`) runs these checks plus a headless-Chrome Mermaid render check (`scripts/check_mermaid.mjs`) on every push and pull request. Nothing is deployed or hosted.

## Layout

```text
docs/                 Markdown source, one folder per section (see zensical.toml nav)
zensical.toml         site, theme, navigation, Markdown extensions
pyproject.toml uv.lock  the pinned Zensical toolchain
baseline.toml         the current baseline, defined once
docs/evidence/        archived acceptance evidence and SHA256SUMS
scripts/              check_links.py, check_content.py, check_baseline.py, check_commands.py, check_mermaid.mjs
.github/workflows/    docs.yml (build and checks only)
```

The first commit of this repository preserves the original bootstrap wiki (verified against devkit v0.2.0); the manual was rewritten from the released sources in the next commit. Maintenance rules: `docs/reference/maintenance.md`.

## Privacy, security and licence

The manual contains no credentials or personal data; `scripts/check_content.py` enforces this in CI. Examples use placeholders (`my-app`, `OWNER`, `example.com`) and paths relative to a directory such as `~/Developer`. Report security issues privately as described in [SECURITY.md](SECURITY.md).

Licensed under the [MIT License](LICENSE).
