# Developer Platform Manual

The private owner, operator and developer manual for the accepted Developer Platform baseline:

| Repository | Release | Commit |
|---|---|---|
| `audiophreak/developer-platform` | `v0.8.0` | `e185d6d2c4ac9edde5db7963458c8146e4c229d2` |
| `audiophreak/web-core-template` | `v0.7.0` | `094e35b8b32d6186d609695f940afeb91a9b5990` |
| `audiophreak/native-ios-template` | `v0.1.0` | `cd346a01223f82e629649a71fc4d312e4e5c7746` |

Published acceptance: **151 / 151 gates passed**.

Markdown source in `docs/`, built with [Zensical](https://zensical.org/) into a static site for local browsing. Dark theme by default; Mermaid diagrams.

## Browse it (macOS)

Prerequisites: Git, the GitHub CLI with access to this private repository, [uv](https://docs.astral.sh/uv/), Python 3.11+ (Homebrew `python@3.14` works), and a browser.

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
uv run python scripts/check_content.py     # no secrets, credentials, personal data or machine paths; SHAs consistent
python3 -m http.server 8000 --bind 127.0.0.1 --directory site   # browse the built copy without the dev server
```

CI (`.github/workflows/docs.yml`) runs the same three checks on every push and pull request. Nothing is deployed or hosted.

## Layout

```text
docs/                 Markdown source, one folder per section (see zensical.toml nav)
zensical.toml         site, theme, navigation, Markdown extensions
pyproject.toml uv.lock  the pinned Zensical toolchain
scripts/              check_links.py, check_content.py
.github/workflows/    docs.yml (build and checks only)
```

The first commit of this repository preserves the original bootstrap wiki (verified against devkit v0.2.0); the manual was rewritten from the released sources in the next commit. Maintenance rules: `docs/reference/maintenance.md`.

## Privacy

Keep this repository private. It contains no credentials or personal data (enforced by `scripts/check_content.py`), but it documents private repositories.
