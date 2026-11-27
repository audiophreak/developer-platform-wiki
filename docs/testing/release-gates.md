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

Tag mechanics, from `docs/maintaining.md` (both templates) and `docs/publishing.md`: merge the PR with a **merge commit**, fast-forward local `main`, wait for CI on the merge commit, create an **annotated** tag on it, push the tag, verify `git ls-remote --tags origin` resolves to the merge commit, verify the repository visibility is as intended. Never move or delete a published tag.

## Published-pair acceptance

The final acceptance is a **fail-closed audit** (`audit-wp4.py`, a harness kept outside the repositories on the acceptance workstation): every gate is one argument-list subprocess with no shell; its exit code is asserted and its output checked (test counts, no failures, no skips); a gate depending on a failed one is recorded as BLOCKED, which is also a failure; the process exits 0 only if every gate passed; the evidence file lists every gate.

!!! success "Accepted: 151 / 151 published acceptance gates passed, 0 failed"

### What the 151 gates cover

| Group | Gates | Checks |
|---|---:|---|
| Preflight | 2 | Docker reachable with no containers; **no leftover Docker volumes** (stale volumes keep old passwords) |
| Published repositories | 12 | for each of the three: remote annotated tag → expected commit; remote `main` == expected SHA; repository is **PRIVATE** (the intended visibility at acceptance); `main` CI green on that SHA |
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

## Acceptance of the native v0.1.1 patch: 177 / 177

After `native-ios-template v0.1.1` was tagged, the same fail-closed harness was rerun against the published combination (devkit v0.8.0, web v0.7.0, native v0.1.1) as `audit-native-v0.1.1.py`, derived from the accepted audit with native expectations moved to v0.1.1 and **26 additional gates**:

| Group | Gates | Checks |
|---|---:|---|
| All original groups | 151 | as above, with native tag `v0.1.1` → `f0f4a5a…`, native provenance v0.1.1, and local native `main` at the merge commit |
| Patch gates, per native project (×2) | 10 | no Git-visible file after all native gates **including the Release check**; the Release log kept at `ios/.derived-data/release.log`; `devkit status` after the check; `upgrade --layer native --dry-run` after the check not refused; the generated README documents `devkit upgrade PROJECT --layer native` and no `upgrade-native` |
| Existing v0.1.0 project upgraded | 16 | generate with `--native-template-ref v0.1.0`; `devkit status` reports `native v0.1.0 newer available: v0.1.1`; the v0.1.0 Release check reproduces `?? ios/.derived-data-release.log` and **devkit upgrade refuses** (exit 1); after moving that one file, the dry run plans `v0.1.0 -> v0.1.1`; the upgrade succeeds and changes exactly `.copier-answers.ios.yml`, `ios/README.md`, `ios/scripts/check-release-config.sh`; both layers up to date; the v0.1.1 Release check leaves the tree clean; a later dry run is not refused |
| **Total** | **177** | **177 passed, 0 failed** |

Evidence: `native-v0.1.1-audit.tsv`, archived as `docs/evidence/2026-11-19-native-v0.1.1/native-v0.1.1-audit-ACCEPTED.tsv` (`TOTAL gates 177 passed 177 failed 0`). The real end-to-end scenario passed again for both providers (sign-in, Keychain token, session, CRUD, cross-user denial, server and database restart, relaunch, sign-out, old token 401).

## Acceptance of the documentation closeout

After developer-platform **v0.8.1** and web-core-template **v0.7.1** (documentation-only) were tagged, the harness ran against the released combination (devkit v0.8.1, web v0.7.1, native v0.1.1) as `audit-closeout-v0.8.1.py`, derived from the 177-gate audit:

| Group | Gates | Checks |
|---|---:|---|
| The 177 gates of the native v0.1.1 audit | 177 | expectations moved to the new releases: platform clone at `v0.8.1` (`fc46434…`), `devkit --version` = `devkit 0.8.1`, web provenance `v0.7.1`, native `v0.1.1`; every project, database, native, end-to-end, upgrade (native v0.1.0 → v0.1.1), parity and untouched-repository gate |
| Byte identity with the previous web release | 15 | each of the five acceptance projects regenerated with the released devkit at `--template-ref v0.7.0`, same name and answers: every generated file byte-identical (24, 106, 106, 185 and 185 files), and `.copier-answers.yml` differing only in `_commit` |
| **Total** | **192** | **192 passed, 0 failed** |

Project names carry a `co-` prefix so the run can never reuse a database volume left by an earlier run; the preflight rejects leftovers for those names only and deletes nothing. The OpenAPI contract of both native projects regenerated byte-identically (`a42effbd…`, the same contract as v0.7.0). Evidence: [Acceptance evidence](../reference/acceptance-evidence.md).

## Running an acceptance yourself

The audit script lives outside the repositories and is not part of any release; sanitized copies are archived in `docs/evidence/`. Its structure is reproducible from the table above: work in a fresh `tools/scratch.py new` workspace, clone the platform at its tag, generate every profile × provider from GitHub, and assert each gate with exit codes and parsed counts. Before starting: no running containers and no leftover volumes for these projects. A completed run leaves its projects' named volumes behind (`db:down` keeps data by design), so the next run's preflight requires removing them first, deliberately.
