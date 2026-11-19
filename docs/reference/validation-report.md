# Validation report

Validation of this manual before publication, 2026-11-19, and its revalidation for the native v0.1.1 baseline update.

## Revalidation: documentation closeout (current baseline)

devkit v0.8.1, web v0.7.1, native v0.1.1.

| Check | Result |
|---|---|
| Strict build | no issues (it caught two anchors to sections not yet written during the update) |
| Links and anchors | 69 pages in navigation; 170 links and anchors resolve |
| Content and security | 87 files clean, including every archived evidence file and `SHA256SUMS`; SHAs read from `baseline.toml`; unfilled `*_RESULT` placeholders rejected |
| Current baseline (`check_baseline.py`, new) | 48 references agree with `baseline.toml`; a negative control restoring the stale footer (native v0.1.0) fails it |
| devkit command syntax (`check_commands.py`, new) | every devkit command in code is valid for devkit 0.8.x; its self-test rejects four invalid commands |
| Mermaid (`check_mermaid.mjs`, now in CI) | 22 / 22 diagrams render; per-page counts come from the Markdown |
| Evidence integrity | `shasum -a 256 -c` passes for every archived file |

## Revalidation: native-ios-template v0.1.1

| Check | Result |
|---|---|
| Strict build (`zensical build --clean --strict`) | **No issues found** |
| Internal links and anchors (`check_links.py`) | 68 pages in navigation; **156** links and anchors resolve |
| Content and security scan (`check_content.py`) | clean; current native SHA `f0f4a5a…`, with v0.1.0's commit and tag object allowed as history |
| Mermaid rendering (headless Chrome, closed shadow roots pierced) | **22 / 22** rendered, 0 errors, two consecutive runs; the probe now also requires each page to render exactly the number of diagrams in its Markdown source (a negative control with a wrong count fails) |
| devkit syntax in examples | every `devkit` invocation in the wiki's code spans and blocks (176) checked with native v0.1.1's own validator (`tests/test_docs_commands.py`); no invalid command; every native upgrade example uses `devkit upgrade PROJECT --layer native` |
| Facts | v0.1.1 tag → `f0f4a5a…` (tag object `8591c9c…`) and v0.1.0 → `cd346a0…` via the GitHub API; native repository private; 58 tests collected at v0.1.1; acceptance evidence `TOTAL gates 177 passed 177 failed 0` |
| Architecture diagrams | structure unchanged (the patch changed no architecture); only the native version label in two diagrams moved from v0.1.0 to v0.1.1 |

## Original validation (native v0.1.0 baseline)

## Build

| Check | Result |
|---|---|
| `uv run zensical build --clean --strict` (Zensical 0.0.74) | **No issues found** (strict mode aborts on any warning) |
| Pages | 68, all in the explicit navigation; no page outside it |
| Navigation | 13 top-level tabs (Home + the 11 required sections + Reference); all visible without overflow at 1280 px and wider; below that the sidebar takes over |

## Links

`scripts/check_links.py`: every navigation target exists, every page is in the navigation, and **every internal link and `#anchor` resolves** (153 links at publication). A planted broken link and a planted missing anchor were both caught (negative control).

## Diagrams

22 Mermaid diagrams (18 flowcharts, 3 sequence diagrams, 1 timeline), and the build contains exactly 22 Mermaid placeholders.

**Rendering verified in a real browser**: the built site was served locally and loaded in headless Chrome 157; for every page with a diagram, a DevTools-protocol probe confirmed each diagram was replaced by a rendered host, pierced the theme's closed shadow roots to find each diagram's SVG, and checked none is Mermaid's error SVG. The first run caught **two real parse errors** (a hyphenated label inside a dotted edge; a `;` in a sequence message); both were fixed and the final run reported **22 rendered, 0 errors, 0 unrendered**. Screenshots were reviewed for legibility in dark mode.

| Required diagram | Page |
|---|---|
| 1. Overall repository and template architecture | [Platform Architecture](../architecture/index.md) (also the home page) |
| 2. New project generation flow | [Generation flow and atomicity](../architecture/generation-flow.md) |
| 3. Full-stack runtime architecture | [Web Application](../web/index.md) |
| 4. Browser authentication flow | [Authentication and sessions](../web/authentication.md) |
| 5. Native iOS authentication flow | [Authentication and the Keychain](../ios/authentication.md) |
| 6. OpenAPI → Swift client generation | [Generated API client](../ios/api-client.md) (and [OpenAPI and Swift](../commands/openapi-swift.md)) |
| 7. Database authorization / RLS flow | [Authorization and row-level security](../web/authorization.md) |
| 8. Layered upgrade workflow | [Upgrade and Recovery](../upgrade/index.md) |
| 9. Local validation → CI → release → published acceptance | [Testing hierarchy](../testing/index.md) |
| 10. AI-assisted development workflow | [The AI-assisted workflow](../ai-workflow/index.md) |

Additional diagrams: the tools interoperation map, the command workflow map, feature dependencies, generated-project ownership, trust boundaries, the native app structure, the getting-started path, the daily workflow, the CRUD sequence, and the release timeline.

## Theme and code

| Check | Result |
|---|---|
| Dark theme | every checked page loads with `data-md-color-scheme="slate"` (dark) and a dark body background; the header toggle switches to light |
| Syntax highlighting | code blocks render with Pygments token spans (for example 213 highlighted spans on the devkit page, 280 on the RLS page) |
| Copy buttons | enabled (`content.code.copy`) |

## Content safety

`scripts/check_content.py` over `docs/`, `scripts/`, configuration and README: **no tokens, private keys, cloud key ids, JWTs, credentialed URLs, home-directory or temporary machine paths, personal email addresses or device UDIDs**, and every full 40-hex SHA is either a baseline commit, a baseline tag object or an allowed action pin. A planted token, home path, UDID and unknown SHA were all caught (negative control). The only credential-shaped value in the manual is the Supabase CLI's *documented, public* local default (`postgres:postgres@127.0.0.1:54322`), explicitly allowed.

## Facts verified against the implementation

| What | How |
|---|---|
| Release tags and commits | GitHub API: tag ref → annotated tag object → commit, for all three; local checkouts clean at those commits |
| Repository visibility | all three `private` |
| `devkit` commands and flags | `--help` captured from v0.8.0; every devkit flag in the manual found in it |
| `devkit` behaviour | live runs against the published templates (see the [source map](source-map.md#live-verification-performed)) |
| Copier flags | `copier copy/update --help` (9.19.1); every Copier flag in the manual found in it |
| npm scripts | every `npm run …` in the manual exists in a freshly generated native-ios project's `package.json` |
| iOS scripts | every `ios/scripts/…` in the manual exists in a freshly generated project |
| Xcode / simctl commands | `xcodebuild -help`, `xcrun simctl help` on Xcode 27.2 |
| Versions and pins | `package.json.jinja`, `Package.swift`, `pyproject.toml`, `docs/dependencies.md` at the tags |
| Test counts | `pytest --collect-only` at the tags; generated-project counts from the acceptance evidence |
| Acceptance | the final evidence file: `TOTAL gates 151 passed 151 failed 0` |

Not re-executed for this manual: `npm ci`/`npm run check`/`test:db` in generated projects, Xcode builds and tests, and the native e2e; their results are taken from the 151-gate acceptance evidence.

## Publication checks

Recorded in the publication commit's message and the final report: repository created private, pushed, visibility re-checked, and a fresh clone built with `--strict` and served.
