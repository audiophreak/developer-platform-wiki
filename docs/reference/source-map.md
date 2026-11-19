# Source verification map

This manual was written on 2026-11-19 from the released source and verified against it. The previous version of this wiki (verified against devkit `v0.2.0` and template `v0.1.0`) is preserved as the first commit of this repository and was not reused where the implementation had moved on.

## Release revisions verified

| Repository | Tag | Tag object | Commit | Verified by |
|---|---|---|---|---|
| developer-platform | **`v0.8.1`** (current) | `8a72aabe194864de03c44a9d8cad0cd0b6ebe058` | `fc464344099bb96b1a58a590c4460e4ead9b1b51` | GitHub API; documentation-only release, CI green on the PR and on `main` |
| developer-platform | `v0.8.0` (original accepted release) | `13d9dd6b81954fcd4439f8147630449deb983f50` | `e185d6d2c4ac9edde5db7963458c8146e4c229d2` | GitHub API (`git/ref/tags` → `git/tags`), local clean checkout `HEAD` |
| web-core-template | **`v0.7.1`** (current) | `547e81958cd5c63e5f58304d91a13bb00e25fa21` | `f704572c35147597a24c2b1eb9b99dae332ea05b` | GitHub API; documentation-only release, CI green on the PR and on `main` |
| web-core-template | `v0.7.0` (original accepted release) | `90e09368844de6c1f81f3d87547980bcbf442289` | `094e35b8b32d6186d609695f940afeb91a9b5990` | same |
| native-ios-template | **`v0.1.1`** (current) | `8591c9cd48b829563c74b4cdccec1ce14082e2d5` | `f0f4a5a8ac58825e94a38068df1bdd413d2f1596` | same; native CI green on the PR and on `main` |
| native-ios-template | `v0.1.0` (original accepted release, superseded) | `97a3a7ce531b93e01507a8d88da0f88de79d2372` | `cd346a01223f82e629649a71fc4d312e4e5c7746` | same; tag unchanged |

All three repositories reported `visibility: private` and default branch `main`. The source repositories were inspected read-only; their working trees were clean before and after.

## Sources by section

| Manual section | Primary sources |
|---|---|
| Getting Started | platform `README.md`, `docs/usage.md`, `Brewfile`, `src/devkit/doctor.py`, `cli.py`; template `README.md`; generated `README.md`, `AGENTS.md`, `docs/*.md`; native `ios/README.md` |
| Command Reference | `devkit --help` output (captured live from v0.8.0); `copier update --help` (9.19.1); generated `package.json`; `scripts/db/cli.mjs`; `ios/scripts/*.sh`, `e2e.mjs` |
| Tools | `pyproject.toml`/`uv.lock` (all repos), `template/package.json.jinja`, `Package.swift`, `docs/dependencies.md`, `docs/architecture.md` |
| Platform Architecture | `src/devkit/*.py`, `docs/architecture.md`, `docs/feature-composition.md`, `docs/native-ios.md`, `docs/release-strategy.md`, `copier.yml` (both), `features.yml`, `tools/*.py`, `tests/contracts/` |
| Web Application | generated `docs/api-v1.md`, `database.md`, `auth.md`, `native-client.md`; `auth.ts.jinja`, `scope.ts`, `guard.ts`, migrations, `compose.yaml`, `supabase/config.toml.jinja`, `next.config.ts.jinja` |
| Native iOS | `template/ios/**` Swift sources, tests, xcconfigs, plists, scripts, `AGENTS.md`, `README.md`; `CHANGELOG.md`; `docs/dependencies.md` |
| Testing and CI | the three `.github/workflows/ci.yml`, generated `ci.yml.jinja`, `docs/ci-evidence.md` (platform, web), `pytest --collect-only` at the tags, acceptance evidence |
| Upgrade and Recovery | `upgrade.py`, `layers.py`, `generate.py`, template `docs/upgrading.md` |
| Troubleshooting | source as labelled per entry; acceptance evidence runs 1–3; owner-reported items marked as such |
| AI workflow | the five `AGENTS.md`/`CLAUDE.md` files, `docs/NEXT_SESSION.md`, `docs/milestone-release-hardening.md` |
| Releases | tags and tag dates, the three `CHANGELOG.md` files, acceptance evidence |

## Live verification performed

!!! note "Historical evidence (original baseline, 2026-11-19)"
    This subsection records the verification run when the manual was first written, against devkit **v0.8.0**, web **v0.7.0** and native **v0.1.0**. Its version numbers are those of that run, not the current baseline. Current-baseline verification is in [Verification of the closeout baseline](#verification-of-the-closeout-baseline).

Run against the released `devkit` v0.8.0 in a disposable directory outside every repository, with the published templates from GitHub:

- `devkit doctor` (exit 0, output reproduced in [setup](../getting-started/setup.md));
- `devkit new` for `web-core`, `full-stack --set database=postgres` (dry run), `full-stack --set database=supabase`, and `native-ios --set database=postgres`: answers files recorded `_commit: v0.7.0` / `v0.1.0` and the GitHub URLs;
- the refusals quoted in this manual (missing database, `auth=false`, `forms` without `zod`, `--native-set` on web-core, existing destination, `native_client` with `--template-ref v0.6.1`);
- `devkit status` (both layers up to date); `upgrade` without `--layer` (exit 2); `--layer web|native --dry-run` (up to date); sticky `database` and `auth` refusals; dirty-tree refusal (exit 1);
- a real upgrade `v0.6.1 → v0.7.0` of a web-core project with a local edit (edit preserved; only `.copier-answers.yml` changed);
- `devkit native add` refused while `native_client` was off, then succeeded after `upgrade --set native_client=true` and a commit, adding only `ios/` and `.copier-answers.ios.yml`.

Not re-run for this manual (taken from the 151-gate acceptance evidence instead): `npm ci`, `npm run check`, `test:db`, Xcode builds and tests, and `e2e.mjs`.

## Known discrepancies in the source repositories

The manual documents the **code's** behaviour. At the current baseline (devkit v0.8.1, web v0.7.1, native v0.1.1) **no known discrepancy between the repositories' documentation and their code remains open.** Earlier ones and the releases that fixed them:

### Resolved in developer-platform v0.8.1 and web-core-template v0.7.1

Documentation-only releases; code, templates, generated output and compatibility are unchanged ([details](../releases/index.md#the-documentation-closeout-v081-and-v071)).

| Where (before) | Was | Now |
|---|---|---|
| `web-core-template/README.md` (v0.7.0) | "everything, 129 tests"; e2e "generates five apps"; fast selection `-m "not e2e"` (which also ran the Docker tests) | the `e2e` and `db` markers, `-m "not e2e and not db"` as the fast selection, the 21 combinations of the main e2e test, counts at 0.7.x (919: 780 / 32 / 109) and `pytest --collect-only -q` for the current number |
| `developer-platform/README.md` (v0.8.0) | "one of two repositories" | one of **three** source repositories, with the one-way dependency and the 0.8.x ranges |
| `developer-platform/docs/usage.md` (v0.8.0) | range `>=0.1.0,<0.7.0 … at devkit 0.7.0` | `>=0.1.0,<0.8.0` (web) and `>=0.1.0,<0.2.0` (native), plus the two-layer rules |
| `developer-platform/docs/ci-evidence.md` (v0.8.0) | "Twenty-six tests … skip in CI" | 28 `integration` tests at 0.8.x (26 web, 2 native pair), with the command that prints the current number |
| `developer-platform/Brewfile` (v0.8.0) | Docker cask commented under a stale "Later milestones" note | states that Docker is required for local database work, the template `db` tests and the native e2e, and optional otherwise; still not installed by the file; `devkit doctor` unchanged (warn) |

### Resolved in native-ios-template v0.1.1

These were listed here at the original baseline and are fixed in the current release (see [the patch](../releases/index.md#the-native-v011-corrective-patch)):

| Where (v0.1.0) | Was | Now (v0.1.1) |
|---|---|---|
| generated `ios/README.md` | named a devkit subcommand that does not exist | documents `devkit status PROJECT` and `devkit upgrade PROJECT --layer native` / `--layer web`; a regression test checks every documented devkit command |
| `native-ios-template/README.md` | a `devkit new` example with a non-existent database flag | `devkit new NAME --profile native-ios --set database=postgres` |
| `ios/scripts/check-release-config.sh` | wrote the un-ignored `ios/.derived-data-release.log` | writes `ios/.derived-data/release.log` (ignored); Xcode tests prove a committed project stays clean |

## Verification of the v0.1.1 update

- Tag `v0.1.1` → `f0f4a5a…` via the GitHub API; `v0.1.0` still → `cd346a0…`; repository private.
- `git diff v0.1.0 v0.1.1` touches only `CHANGELOG.md`, `README.md`, `template/ios/README.md.jinja`, `template/ios/scripts/check-release-config.sh` and two test files.
- `pytest --collect-only` at `v0.1.1`: 58 tests (51 non-Xcode, 7 Xcode).
- Published acceptance of devkit v0.8.0 + web v0.7.0 + native v0.1.1: **177 / 177** ([details](../testing/release-gates.md#acceptance-of-the-native-v011-patch-177-177)).
- No devkit or web-core-template change was needed or made.

## Verification of the closeout baseline

Current baseline: devkit **v0.8.1**, web **v0.7.1**, native **v0.1.1** (defined once in `baseline.toml`).

- Tags via the GitHub API: `v0.8.1` → `fc46434…` (tag object `8a72aab…`), `v0.7.1` → `f704572…` (tag object `547e819…`), `v0.1.1` → `f0f4a5a…`; every earlier tag unchanged; all three repositories private; CI green on each release PR and on `main`.
- developer-platform v0.8.1 vs v0.8.0: only `__version__` changes under `src/`; `devkit --help` for every subcommand and the serialized profile registry are byte-identical; no snapshot changed; `uv run pytest` 502 passed + the live gate (`-m integration`) 28 passed with both templates checked out at their released tags; `capture_contract.py --check` passes for web 0.7.0 and native 0.1.0, and neither template's `copier.yml` (nor web's `.nvmrc`) changed since those releases.
- web-core-template v0.7.1 vs v0.7.0: only `README.md`, `CHANGELOG.md` and `docs/ci-evidence.md` change; `compare_release.py v0.7.0` reports all 42 valid configurations identical; `REQUIRE_DOCKER=1 uv run pytest` 919 passed; `refresh_locks.py --check --before=2026-11-04` reproduces all 11 lockfiles.
- Published acceptance of the released combination: **192 / 192**, including byte identity of every acceptance project against web v0.7.0 ([release gates](../testing/release-gates.md#acceptance-of-the-documentation-closeout)).
- This manual: `scripts/check_baseline.py` checks 48 current-baseline references against `baseline.toml`; `scripts/check_commands.py` checks every devkit command in code against devkit 0.8.x.

## Facts that could not be documented conclusively

- **Owner-reported troubleshooting items** (Homebrew architecture, Intel vs ARM, Node path, `-runFirstLaunch`, `DTServiceHubClient failed to bless service hub`, SpringBoard/PosterBoard): these are not recorded in any repository or in the acceptance evidence. Their entries give the toolchain's documented behaviour and safe recoveries, and are labelled *owner-reported*.
- **The exact Xcode version used by each acceptance run** is not recorded in the evidence TSVs; the acceptance workstation currently has Xcode 27.2, and the native template's CI uses the newest Xcode 26 on `macos-26`.
- **devkit 0.1.0** has no tag in the current repository (it predates the split); its contents are known only from `CHANGELOG.md`.
- **Hosted-test counting**: the acceptance run reports 11 hosted tests passing; in a normal `test.sh app` run, 3 of them (the end-to-end phases and marker) are disabled by `E2E_PHASE` and are counted by Swift Testing's summary.
- **Earlier work packages (WP1, WP2)** are not named in the repositories; only WP3 and WP4 are.
