# Accepted baseline

!!! success "Status: ACCEPTED — documentation closeout (devkit v0.8.1, web v0.7.1, native v0.1.1): 192 / 192 published acceptance gates passed, 0 failed"

| Repository | Release | Commit | Tagged (UTC) | Visibility |
|---|---|---|---|---|
| `audiophreak/web-core-template` | **`v0.7.1`** | `f704572c35147597a24c2b1eb9b99dae332ea05b` | 2026-11-19 20:14 | private |
| `audiophreak/native-ios-template` | **`v0.1.1`** | `f0f4a5a8ac58825e94a38068df1bdd413d2f1596` | 2026-11-19 18:06 | private |
| `audiophreak/developer-platform` | **`v0.8.1`** | `fc464344099bb96b1a58a590c4460e4ead9b1b51` | 2026-11-19 20:17 | private |

All three are annotated tags; the commits above are the tag targets, verified against GitHub (`git/ref/tags` → `git/tags` → `object.sha`) and against clean local checkouts whose `main` equals the tag.

Compatibility is unchanged across every release since the original baseline: devkit 0.8.x supports web `>=0.1.0,<0.8.0` (0.7.x current) and native `>=0.1.0,<0.2.0` (0.1.x), and pairs native 0.1.x with web `>=0.7.0,<0.8.0`. The registry, the CLI and the contract snapshots of v0.8.1 are identical to v0.8.0.

## The documentation closeout (v0.8.1 and v0.7.1)

An independent read-only audit after the native patch found documentation drift in the source repositories (not an implementation defect). Two **documentation-only** releases corrected it; nothing that generates, validates or upgrades a project changed:

| Release | Corrections | Proof of no functional change |
|---|---|---|
| developer-platform **v0.8.1** ([PR #9](https://github.com/audiophreak/developer-platform/pull/9), merge `fc46434`) | README: one of **three** source repositories; `docs/usage.md`: upgrade range `>=0.1.0,<0.8.0` (web) and `>=0.1.0,<0.2.0` (native) instead of the 0.7.0-era `<0.7.0`, plus the two-layer rules; `docs/ci-evidence.md`: 28 integration tests skip in CI (26 web, 2 native pair), not 26, and the negative-control probe's provenance; `Brewfile`: when Docker is required and that it stays optional | only `__version__` changes under `src/`; `devkit --help` for every subcommand and the serialized profile registry byte-identical to v0.8.0; snapshots untouched and verified against their tags; 502 passed + the live gate 28/28 with both templates on released tags |
| web-core-template **v0.7.1** ([PR #12](https://github.com/audiophreak/web-core-template/pull/12), merge `f704572`) | README "Tests": the suite's markers and real counts (919: 780 / 32 `e2e` / 109 `db`) instead of "129 tests" and "five apps", and the correct fast selection `-m "not e2e and not db"`; `docs/ci-evidence.md`: the negative-control probe's provenance | nothing under `template/`, `copier.yml`, `features.yml`, `locks/` or `tools/` changed; all **42** valid configurations render byte-identically to v0.7.0 (`compare_release.py`); 919 passed with Docker required |

native-ios-template stays at **v0.1.1**. Published acceptance of the released combination: **192 / 192** gates ([details](../testing/release-gates.md#acceptance-of-the-documentation-closeout)), including byte-identity of every acceptance project generated at web v0.7.1 against the same project generated at web v0.7.0.

## Baseline history

| Baseline | developer-platform | web-core-template | native-ios-template | Acceptance |
|---|---|---|---|---|
| **Current** (2026-11-19, closeout) | `v0.8.1` (`fc46434`) | `v0.7.1` (`f704572`) | **`v0.1.1`** (`f0f4a5a`) | **192 / 192** |
| Native patch (2026-11-19) | `v0.8.0` | `v0.7.0` | `v0.1.1` (`f0f4a5a`, tag object `8591c9c`) | 177 / 177 |
| Original accepted (2026-11-19) | `v0.8.0` | `v0.7.0` | `v0.1.0` (`cd346a0`, tag object `97a3a7c`) | 151 / 151 |

`v0.1.0` remains published and unchanged; it is superseded, not withdrawn.

## The native v0.1.1 corrective patch

Two defects in `v0.1.0`, found while writing this manual, fixed without any change to the contract, the generated client, Swift sources, the Xcode project, configuration, dependencies, authentication or app behaviour ([PR #2](https://github.com/audiophreak/native-ios-template/pull/2), merge commit `f0f4a5a`):

| Defect in v0.1.0 | Correction in v0.1.1 |
|---|---|
| The generated `ios/README.md` named a devkit subcommand that does not exist | It documents the real layered workflow: `devkit status PROJECT`, `devkit upgrade PROJECT --layer native` / `--layer web` (with `--dry-run`), and the raw `copier update --answers-file .copier-answers.ios.yml …`. The repository README's `devkit new` example used a non-existent database flag; it is now `--set database=postgres`. |
| `ios/scripts/check-release-config.sh` wrote `ios/.derived-data-release.log`, an un-ignored file, so running the check made a committed project dirty and the next `devkit upgrade` refused it | The log is `ios/.derived-data/release.log`, inside the ignored build area; on failure the last 30 lines are still printed and the log is named |

Only `ios/README.md` and `ios/scripts/check-release-config.sh` change in generated projects (plus `_commit` in `.copier-answers.ios.yml`). Regression tests: `tests/test_docs_commands.py` (13) and two Xcode tests (a committed project stays clean after the Release check, passing and failing); all five fail against the v0.1.0 files. Native CI passed on the PR and on `main`; the template suite is 58 tests. Upgrade an existing project with [`devkit upgrade PROJECT --layer native`](../upgrade/layers.md#upgrading-a-v010-native-layer-to-v011).

## What the baseline can do

| Capability | Where |
|---|---|
| Read-only workstation check (Python, Copier, Git, Node 26, uv, gh, credentials, Docker, Xcode 26+, simulator runtime, Brewfile) | `devkit doctor` |
| Generate `web-core`, `full-stack` (postgres \| supabase) and `native-ios` projects from published releases, atomically for two layers | `devkit new` |
| Show and upgrade each layer separately, with range, pair, sticky and clean-tree protections | `devkit status`, `devkit upgrade --layer` |
| Add the native layer to a full-stack project | `devkit native add` |
| Next.js 16 + React 19 + strict TS + Tailwind 4 + shadcn/ui + ESLint + Prettier + Vitest + CI | web-core-template |
| Zod, React Hook Form, REST API v1 with RFC 9457 errors | `zod`, `forms`, `rest_api` |
| PostgreSQL 17 via Docker Compose or local Supabase, SQL migrations with a checksum lock, server-only data layer | `database` |
| Better Auth on PostgreSQL for both providers, `app_runtime` least privilege, RLS owner scoping, protected API | `auth` |
| Bearer tokens for native clients, deterministic OpenAPI 3.1 contract with drift tests | `native_client` |
| SwiftUI iOS 17 app, generated Swift client, Keychain token storage, rotation, restoration, CRUD, sign-out, Release https only | native-ios-template |

## Toolchain pinned by the baseline

| Area | Pins |
|---|---|
| Python side | Python ≥ 3.12 (CI 3.12, 3.14), uv 0.13.6 in CI, Copier 9.19.1, pytest 9.2.0 |
| Web | Node 26 (`>=26 <27`), Next.js 16.4.5, React 19.3.0, TypeScript 5.9.3, Tailwind 4.3.5, ESLint 9.39.5, Prettier 3.9.10, Vitest 5.0.5, Zod 4.6.7, React Hook Form 7.91.0, pg 8.23.1, Better Auth 1.7.16, Supabase CLI 2.122.1, `postgres:17.10` by digest |
| Native | Xcode 26+, iOS 17.0, Swift 6, swift-openapi-generator 1.14.3, swift-openapi-runtime 1.13.4, swift-openapi-urlsession 1.4.0, swift-http-types 1.8.0, swift-collections 1.7.5 |

## Acceptance

The current combination passed a **192-gate** fail-closed audit: the 177 gates below at the new versions plus 15 byte-identity gates (each acceptance project generated at web v0.7.1 equals the same project generated at web v0.7.0, apart from `_commit`). Before it, native v0.1.1 passed a **177-gate** audit: every gate of the original 151-gate audit with native expectations moved to v0.1.1, plus the patch's gates (no Git-visible file after the Release check, `devkit status` and a native upgrade dry run not refused afterwards, the README's command) and a real v0.1.0 → v0.1.1 upgrade of an existing project. The original audit cloned the platform at `v0.8.0`, generated five projects from GitHub (one `web-core`, two `full-stack`, two `native-ios`, one per database provider), and passed every gate: provenance, refusals, `npm run check`, audits, real databases, the native layer's checks, the real end-to-end scenario on the simulator for both providers, provider parity, and proof that the source repositories were not modified. Details: [Release gates and acceptance](../testing/release-gates.md).

## Known limitations of the baseline

- Local development only: no deployment configuration, no hosted database, no mail service; open public registration is not ready (see the generated `docs/auth.md`).
- `devkit upgrade` goes to one target release per run and cannot switch features off.
- The native e2e and the platform's live contract gate run locally, not in CI.
- Branch protection is not configured (private repositories on the Free plan).
