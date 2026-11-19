# Release gates and acceptance

A **release gate** is a check that must pass before a tag is created but cannot (or deliberately does not) run in CI. **Published-pair acceptance** runs after tagging, against the published repositories only, and decides whether a baseline is accepted.

## Gates before tagging

| Repository | Gate | Command |
|---|---|---|
| web-core-template | full suite including e2e | `uv run --locked pytest` |
| | real databases (for database/auth changes) | `uv run pytest -m db` (Docker running) |
| | default output unchanged vs previous tag | `uv run python tools/compare_release.py <previous tag>` |
| | every lockfile derivable and additive | `uv run python tools/refresh_locks.py --check` |
| | CI green on 3.12 and 3.14 on the PR, then on the merge commit | `gh pr checks`, `gh run watch` |
| native-ios-template | full suite including Xcode | `uv run pytest` |
| | Xcode project not drifted | `uv run python tools/gen_pbxproj.py --check` |
| | **real e2e on both providers** | `node ios/scripts/e2e.mjs` in a `native-ios` project per provider |
| developer-platform | snapshot captured **from the new tag** and verified | `tools/capture_contract.py --ref vX.Y.Z --write` then `--check` |
| | live contract gate | `uv run pytest -m integration` (checkouts beside it) |
| | full suite, CI green | `uv run --locked pytest` |

Tag mechanics, from `docs/maintaining.md` (both templates) and `docs/publishing.md`: merge the PR with a **merge commit**, fast-forward local `main`, wait for CI on the merge commit, create an **annotated** tag on it, push the tag, verify `git ls-remote --tags origin` resolves to the merge commit, verify the repository is still private. Never move or delete a published tag.

## Published-pair acceptance

The final acceptance is a **fail-closed audit** (`~/Claude/audit-wp4.py` on the owner's workstation): every gate is one argument-list subprocess with no shell; its exit code is asserted and its output checked (test counts, no failures, no skips); a gate depending on a failed one is recorded as BLOCKED, which is also a failure; the process exits 0 only if every gate passed; the evidence file lists every gate.

!!! success "Accepted: 151 / 151 published acceptance gates passed, 0 failed"

### What the 151 gates cover

| Group | Gates | Checks |
|---|---:|---|
| Preflight | 2 | Docker reachable with no containers; **no leftover Docker volumes** (stale volumes keep old passwords) |
| Published repositories | 12 | for each of the three: remote annotated tag → expected commit; remote `main` == expected SHA; repository is **PRIVATE**; `main` CI green on that SHA |
| Platform from a fresh clone | 5 | clone tag `v0.8.0`; HEAD == `e185d6d…`; `uv sync --locked`; `devkit --version` = 0.8.0; `devkit doctor` |
| Generation from GitHub | 17 | `devkit new` for `basic-app` (web-core), `fs-pg`, `fs-sb` (full-stack × provider), `nat-pg`, `nat-sb` (native-ios × provider); web provenance = published v0.7.0 (not a path); native provenance = published v0.1.0; baseline committed |
| Refusals | 8 | full-stack without a database; full-stack with `auth=false`; native-ios without a database; `--native-set` on web-core: each **exit 2 and created nothing** |
| Web validation | 41 | per project: `npm ci`; `npm run check` (3 / 248 / 248 / 257 / 257 tests, none failed or skipped); `npm audit --omit=dev` = 0 vulnerabilities; no credentials; no personal paths or names; upgrade dry-run up to date; tree clean afterwards; native projects also: `devkit status` both layers up to date, upgrade without `--layer` refused (exit 2), `--layer web` and `--layer native` dry-runs up to date |
| Real databases | 24 | per full-stack/native project: `db:init`, `db:up`, `db:migrate`, `db:status` (3 migrations applied, none pending, runtime role `app_runtime`), `test:db` (70 passed), `db:down` |
| Native layer | 22 | per native project: deterministic `openapi:generate`; contract byte-identical after regeneration; web `openapi.json` == iOS `Contract/openapi.json`; static checks; contract check; client regeneration zero diff; host `swift test` 58; simulator package tests 58; simulator hosted app + Keychain 11; Release HTTPS/ATS; committed client == fresh generation |
| Native end-to-end | 14 | per native project: `e2e.mjs` exit 0; phase one (sign-in, Keychain token, session, create/read/update, cross-user denial); server **and database restart**; phase two (relaunch persistence, delete, sign-out, old token 401); **no token in the server log**; scenario verdict; no test skipped |
| Provider parity | 3 | `openapi.json` identical across all four full-stack/native projects; `ios/` identical between providers apart from the name; both providers passed the same e2e |
| Source repositories untouched | 3 | local HEAD, status, tags and branches of the three source repositories unchanged by the audit |
| **Total** | **151** | **151 passed, 0 failed** |

### How acceptance was reached

The evidence directory holds three runs of the same audit:

| Run | Result | What failed | Resolution |
|---|---|---|---|
| 1 | 143 / 149 | the audit's own skip detection counted Xcode's `appintentsmetadataprocessor … Metadata extraction skipped` warning as a skipped test; parity compared `ios/` trees without normalizing the app name | audit checks corrected; no product change |
| 2 | 135 / 149 | `db:migrate` → `cannot connect to the database (28P01)` in the two postgres projects, cascading to `test:db`, e2e and parity | **stale Docker volumes** from earlier runs kept the old `POSTGRES_PASSWORD`; a fresh `db:init` generated a new one. The audit gained two preflight gates (no containers, no leftover volumes) |
| 3 | **151 / 151** | – | accepted |

Neither earlier run indicated a defect in the released code; both were environment or audit-harness issues, and each is now a documented [troubleshooting](../troubleshooting/database.md#stale-docker-volumes-and-28p01) entry or a gate.

## Running an acceptance yourself

The audit script lives outside the repositories, in the owner's `~/Claude` directory, and is not part of any release. Its structure is reproducible from the table above: work in a fresh `tools/scratch.py new` workspace, clone the platform at its tag, generate every profile × provider from GitHub, and assert each gate with exit codes and parsed counts. Before starting: no running containers and no leftover volumes for these projects.
