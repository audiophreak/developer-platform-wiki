# Developer Platform Knowledge Base

A private, local-first technical wiki for learning and operating the AI-assisted Developer Platform. Documentation source is Markdown; Zensical builds a static site for local preview in Chrome.

The site opens in dark mode by default; use the header palette toggle to switch to light mode.

## Quick start (macOS)

Prerequisites: Git, Python 3.12 (or compatible Python 3.11+), [uv](https://docs.astral.sh/uv/getting-started/installation/), and Google Chrome.

```bash
cd ~/Developer/developer-platform-wiki
uv sync --locked
uv run zensical serve --open
```

Zensical serves the preview at `http://localhost:8000`. Press `Ctrl+C` to stop it. This server binds to localhost by default and is for preview, not production hosting.

If your default browser is not Chrome, open a second Terminal tab and run `open -a "Google Chrome" http://localhost:8000`.

The archive also includes the prebuilt static site. To browse that snapshot without installing the Python environment, run from this folder:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Then open `http://localhost:8000` in Chrome. Stop it with `Ctrl+C`. Rebuild after editing Markdown to refresh this snapshot.

Build and validation:

```bash
uv run zensical build --strict
python3 scripts/check_links.py
```

## Put it in a private GitHub repository

This bootstrap does not create the remote repository. After extracting and reviewing the archive, you can initialize Git and create the requested private remote from the project folder:

```bash
git init -b main
git add .
git commit -m "docs: bootstrap developer platform wiki"
gh repo create audiophreak/developer-platform-wiki --private --source . --remote origin --push
```

The included Actions workflow runs documentation checks only; it does not publish the site. No hosting or public access is configured.

## Project layout

- `docs/` — source articles and assets
- `zensical.toml` — site, theme, and full explicit navigation
- `pyproject.toml` + `uv.lock` — pinned, reproducible local tooling
- `scripts/check_links.py` — local Markdown-link and navigation target check
- `.github/workflows/docs.yml` — private-repository CI build/link check; does not deploy
- `docs/reference/maintenance.md` — content contribution and freshness workflow

## Source-verification status

The private repositories were reviewed at `developer-platform v0.2.0` and `web-core-template v0.1.0`; see `docs/reference/source-map.md` for commit SHAs and source paths. Draft pull requests are separately identified and are not treated as released behavior. Some future architecture areas remain marked Planned.

## Privacy

Keep the GitHub repository private. This bootstrap configures no remote, publishing workflow, hosting provider, secrets, or repository credentials. Review content for personal paths, private source, internal infrastructure, and secrets before any future sharing.
