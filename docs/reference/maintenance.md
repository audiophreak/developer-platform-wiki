# Maintaining this manual

## Layout

```text
developer-platform-wiki/
├── docs/                    # Markdown source; one folder per top-level section
├── zensical.toml            # site, theme (dark slate default), explicit navigation, Markdown extensions
├── pyproject.toml uv.lock   # zensical (dev group), exact via the lock
├── scripts/check_links.py   # navigation targets, internal links + anchors, Mermaid block/placeholder parity
├── scripts/check_content.py # no secrets, credentials, personal data or machine paths; baseline SHAs consistent
└── .github/workflows/docs.yml   # strict build + both checks on push and PR; no deployment
```

## Local commands

```bash
uv sync --locked
uv run zensical serve --open          # http://localhost:8000, live reload
uv run zensical build --clean --strict
uv run python scripts/check_links.py
uv run python scripts/check_content.py
```

To browse a built copy without the dev server: `python3 -m http.server 8000 --bind 127.0.0.1 --directory site`. Diagrams need network access in the browser (Mermaid is loaded from `unpkg.com` by the theme).

## Writing rules

- **The released source is authoritative.** Verify every behavioural statement against a tag; prefer quoting real command output.
- **Only released behaviour.** Nothing from an unmerged branch.
- **Label uncertainty.** Troubleshooting entries carry an *Evidence* line; unverifiable facts go to the [source map](source-map.md).
- **No secrets, identities or machine paths.** Use `~/Developer/...`, placeholders like `<your home>`, `me@example.test`. `scripts/check_content.py` enforces it.
- **Mermaid:** quote labels containing `--`, `;`, `<` or brackets (`node["a --flag"]`); one idea per diagram; check rendering in the browser.
- **Cross-link** related pages; every new page goes into `nav` in `zensical.toml`.

## Updating for a new baseline

1. Read the three `CHANGELOG.md` files from the previous baseline's tags to the new ones.
2. Update [Accepted baseline](../releases/index.md), [history](../releases/history.md), the home page banner, and `EXPECTED_SHAS` in `scripts/check_content.py`.
3. Re-capture `devkit --help` output and re-run the live verification listed in the [source map](source-map.md#live-verification-performed).
4. Re-check version tables (Tools, Release baseline) against `package.json.jinja`, `Package.swift` and `pyproject.toml`.
5. Re-collect test counts (`pytest --collect-only -q`) at the new tags.
6. Revisit the known-discrepancies table: remove fixed items, add new ones.
7. Build, run both checks, verify in the browser, commit, push.
