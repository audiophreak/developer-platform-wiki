# Maintaining this manual

## Layout

```text
developer-platform-wiki/
├── docs/                    # Markdown source; one folder per top-level section
├── zensical.toml            # site, theme (dark slate default), explicit navigation, Markdown extensions
├── pyproject.toml uv.lock   # zensical (dev group), exact via the lock
├── baseline.toml            # THE current baseline (versions, commits, tag objects) + history + provenance commits
├── docs/evidence/           # archived acceptance evidence (TSVs verbatim, harnesses sanitized) + SHA256SUMS
├── scripts/check_links.py   # navigation targets, internal links + anchors, Mermaid block/placeholder parity
├── scripts/check_content.py # no secrets, credentials, personal data, machine paths or unfilled placeholders; SHAs from baseline.toml
├── scripts/check_baseline.py # every high-authority "current baseline" location agrees with baseline.toml
├── scripts/check_commands.py # every devkit command in code exists in devkit 0.8.x with valid options
├── scripts/check_mermaid.mjs # every diagram renders in headless Chrome (expected counts from the Markdown)
└── .github/workflows/docs.yml   # strict build + every check above on push and PR; no deployment
```

## Local commands

```bash
uv sync --locked
uv run zensical serve --open          # http://localhost:8000, live reload
uv run zensical build --clean --strict
uv run python scripts/check_links.py
uv run python scripts/check_content.py
uv run python scripts/check_baseline.py
uv run python scripts/check_commands.py
# Mermaid: serve site/ on 127.0.0.1:8765, start Chrome with --headless=new --remote-debugging-port=9333, then
node scripts/check_mermaid.mjs http://127.0.0.1:8765 9333
```

CI (`.github/workflows/docs.yml`) runs all of them, Mermaid included.

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
2. Verify the new tags on GitHub, move the old `[current]` entries of `baseline.toml` into `[[history]]` and write the new ones. Then `uv run python scripts/check_baseline.py` lists every current-baseline location that still names the old release; update them, plus [Accepted baseline](../releases/index.md), [history](../releases/history.md) and the home banner.
3. Archive the new acceptance evidence in `docs/evidence/` (TSV verbatim, harness sanitized of personal data), add it to `SHA256SUMS` and [Acceptance evidence](acceptance-evidence.md).
4. Re-capture `devkit --help` output and re-run the live verification listed in the [source map](source-map.md#live-verification-performed).
5. Re-check version tables (Tools, Release baseline) against `package.json.jinja`, `Package.swift` and `pyproject.toml`.
6. Re-collect test counts (`pytest --collect-only -q`) at the new tags.
7. Revisit the known-discrepancies table: remove fixed items, add new ones.
8. Build, run every check, verify in the browser, commit, push.
