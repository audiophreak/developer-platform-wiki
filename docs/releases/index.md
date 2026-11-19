# Accepted baseline

!!! success "Status: ACCEPTED — 151 / 151 published acceptance gates passed, 0 failed"

| Repository | Release | Commit | Tagged (UTC) | Visibility |
|---|---|---|---|---|
| `audiophreak/web-core-template` | **`v0.7.0`** | `094e35b8b32d6186d609695f940afeb91a9b5990` | 2026-11-19 04:11 | private |
| `audiophreak/native-ios-template` | **`v0.1.0`** | `cd346a01223f82e629649a71fc4d312e4e5c7746` | 2026-11-19 04:29 | private |
| `audiophreak/developer-platform` | **`v0.8.0`** | `e185d6d2c4ac9edde5db7963458c8146e4c229d2` | 2026-11-19 04:42 | private |

All three are annotated tags; the commits above are the tag targets, verified against GitHub (`git/ref/tags` → `git/tags` → `object.sha`) and against clean local checkouts whose `main` equals the tag.

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

The published-pair audit cloned the platform at `v0.8.0`, generated five projects from GitHub (one `web-core`, two `full-stack`, two `native-ios`, one per database provider), and passed every gate: provenance, refusals, `npm run check`, audits, real databases, the native layer's checks, the real end-to-end scenario on the simulator for both providers, provider parity, and proof that the source repositories were not modified. Details: [Release gates and acceptance](../testing/release-gates.md).

## Known limitations of the baseline

- Local development only: no deployment configuration, no hosted database, no mail service; open public registration is not ready (see the generated `docs/auth.md`).
- `devkit upgrade` goes to one target release per run and cannot switch features off.
- The native e2e and the platform's live contract gate run locally, not in CI.
- Branch protection is not configured (private repositories on the Free plan).
- Native template `v0.1.0`: `check-release-config.sh` leaves an un-ignored `ios/.derived-data-release.log`; its generated README names a non-existent `devkit upgrade-native` command (see the [source map](../reference/source-map.md#known-discrepancies-in-the-source-repositories)).
