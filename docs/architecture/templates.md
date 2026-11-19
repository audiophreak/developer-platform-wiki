# The two templates

Both are Copier templates with the same conventions: `_subdirectory: template`, `_templates_suffix: .jinja`, `_min_copier_version: "9.19.1"`, **no `_tasks`, `_migrations` or `_jinja_extensions`** (a test enforces it, so `--trust` is never needed), validation only in `copier.yml`, generated output free of secrets, identities and home paths (tests scan it).

## web-core-template

```text
web-core-template/
├── copier.yml          # questions, strict validators, computed has_database / has_server / lock_key
├── features.yml        # registry: requires, conflicts, npm:true|false, choices (tools and tests read it; Copier does not)
├── locks/              # one complete package-lock per distinct npm dependency set (never rendered itself)
│   ├── base.json  zod.json  forms+zod.json
│   ├── database-{postgres,supabase}+zod.json  database-…+forms+zod.json
│   └── auth+database-{postgres,supabase}+zod.json  auth+…+forms+zod.json        # 11 in all
├── template/           # rendered tree; conditional names like {% if auth %}auth{% endif %}
├── tools/              # features.py, refresh_locks.py, compare_release.py
├── tests/              # 919 tests: render, validators, versions, upgrades from real tags, e2e (npm), db (Docker)
└── docs/               # features.md, maintaining.md, upgrading.md, provenance.md, ci-evidence.md
```

### Questions at v0.7.0

| Question | Type | Default | Rule (validator) |
|---|---|---|---|
| `app_name` | str | required | `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, ≤ 64 |
| `app_description` | str | `A Next.js application` | ≤ 200 safe ASCII characters, single spaces |
| `cache_components` | strict bool | `true` | |
| `zod` | strict bool | `false` | |
| `forms` | strict bool | `false` | requires `zod` |
| `rest_api` | strict bool | `false` | requires `zod` |
| `database` | choice `none`/`postgres`/`supabase` | `none` | non-`none` requires `zod` |
| `auth` | strict bool | `false` | requires `zod`, `rest_api`, `database != none` |
| `native_client` | strict bool | `false` | requires `auth` |

Computed, never asked, never recorded: `has_database` (`database != 'none'`), `has_server` (`rest_api or has_database`), `lock_key` (e.g. `auth+database-postgres+zod`).

### How a feature appears in the tree

- **Conditional paths.** A path segment that renders empty is skipped with everything under it: `src/{% if has_server %}server{% endif %}/{% if auth %}auth{% endif %}/…`.
- **Guarded blocks** in shared files (`package.json.jinja`, `AGENTS.md.jinja`, `README.md.jinja`, `ci.yml.jinja`), kept small.
- **The lockfile shim.** `template/package-lock.json.jinja` includes `locks/<lock_key>.json`. Copier's Jinja search path is the repository root, so `locks/` sits outside `template/` and is never rendered itself.

### The lock matrix

Lockfiles needed = distinct npm dependency sets (11), not 2^features. `rest_api` and `native_client` add no npm dependency (`npm: false`) and share locks. `tools/refresh_locks.py` derives each lock from `locks/base.json` with `npm install --package-lock-only --ignore-scripts --before=<two weeks ago>` and refuses any result that is not strictly additive (every base package unchanged in version, source and integrity). Tests check: registry-only sources with integrity hashes, `package.json` match, no orphans, **no new install scripts**, matrix capped at 16.

### Release invariants

With every new feature **off**, output must be byte-identical to the previous tag apart from `.copier-answers.yml` (`tools/compare_release.py <tag>`; rare, exact single-file allowances such as the v0.3.0 `.prettierignore` line are explicit and fail if unused).

## native-ios-template

```text
native-ios-template/
├── copier.yml              # _answers_file: .copier-answers.ios.yml; app_name, app_display_name, bundle_identifier,
│                           #   debug_api_port (int, 1024-65535), release_api_host (host[:port], no scheme)
├── template/ios/           # the ONLY rendered directory (plus the answers file)
│   ├── App/                # SwiftUI views (synchronized folder)
│   ├── AppTests/           # hosted tests: Keychain, build configuration, end-to-end
│   ├── Config/             # Shared/Debug/Release.xcconfig (.jinja), Info-Debug.plist, Info-Release.plist
│   ├── Contract/           # openapi.json (copy of web v0.7.0), openapi.sha256, generator config
│   ├── Packages/AppCore/   # Sources/APIClient (generated), Sources/AppCore, Tests (58)
│   ├── Tools/Generator/    # pinned swift-openapi-generator
│   ├── scripts/            # test, simulator, check-*, generate-client, sync-contract, e2e.mjs
│   └── AGENTS.md CLAUDE.md README.md
├── tools/gen_pbxproj.py    # generates the committed, static App.xcodeproj
├── tools/web_contract.json # {"web_core_template_release": "v0.7.0", "sha256": "a42effbd…"}
└── tests/                  # 43 tests: render, layering, static rules, pins and ages, update; xcode (5)
```

Only `Config/*.xcconfig`, `README.md` and `AGENTS.md` are templated. The Xcode project, Swift sources and the generated client are verbatim, so a rendered project is reviewable and the client can be regenerated with zero diff.

### Layering rules

- It renders **only** `ios/` and `.copier-answers.ios.yml`; tests prove in both directions that neither template writes the other's files.
- The web template knows only that `ios/` *may* exist: its lint and format config exclude it, and its `AGENTS.md` (with `native_client`) tells agents to read `ios/AGENTS.md` and not edit it from web work.
- The native template knows the web contract it was generated from (`tools/web_contract.json`); `ios/scripts/check-contract.sh` compares it to the project's own `openapi/openapi.json`.
