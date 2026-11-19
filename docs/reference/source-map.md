# Source verification map

This manual was written on 2026-11-19 from the released source and verified against it. The previous version of this wiki (verified against devkit `v0.2.0` and template `v0.1.0`) is preserved as the first commit of this repository and was not reused where the implementation had moved on.

## Release revisions verified

| Repository | Tag | Tag object | Commit | Verified by |
|---|---|---|---|---|
| developer-platform | `v0.8.0` | `13d9dd6b81954fcd4439f8147630449deb983f50` | `e185d6d2c4ac9edde5db7963458c8146e4c229d2` | GitHub API (`git/ref/tags` → `git/tags`), local clean checkout `HEAD` |
| web-core-template | `v0.7.0` | `90e09368844de6c1f81f3d87547980bcbf442289` | `094e35b8b32d6186d609695f940afeb91a9b5990` | same |
| native-ios-template | `v0.1.0` | `97a3a7ce531b93e01507a8d88da0f88de79d2372` | `cd346a01223f82e629649a71fc4d312e4e5c7746` | same |

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

Run against the released `devkit` v0.8.0 in a disposable directory outside every repository, with the published templates from GitHub:

- `devkit doctor` (exit 0, output reproduced in [setup](../getting-started/setup.md));
- `devkit new` for `web-core`, `full-stack --set database=postgres` (dry run), `full-stack --set database=supabase`, and `native-ios --set database=postgres`: answers files recorded `_commit: v0.7.0` / `v0.1.0` and the GitHub URLs;
- the refusals quoted in this manual (missing database, `auth=false`, `forms` without `zod`, `--native-set` on web-core, existing destination, `native_client` with `--template-ref v0.6.1`);
- `devkit status` (both layers up to date); `upgrade` without `--layer` (exit 2); `--layer web|native --dry-run` (up to date); sticky `database` and `auth` refusals; dirty-tree refusal (exit 1);
- a real upgrade `v0.6.1 → v0.7.0` of a web-core project with a local edit (edit preserved; only `.copier-answers.yml` changed);
- `devkit native add` refused while `native_client` was off, then succeeded after `upgrade --set native_client=true` and a commit, adding only `ios/` and `.copier-answers.ios.yml`.

Not re-run for this manual (taken from the 151-gate acceptance evidence instead): `npm ci`, `npm run check`, `test:db`, Xcode builds and tests, and `e2e.mjs`.

## Known discrepancies in the source repositories

The manual documents the **code's** behaviour. These repository documents disagree with it and should be corrected in a future release of the repository concerned:

| Where | Says | Actual behaviour at the baseline |
|---|---|---|
| `native-ios-template/README.md` | `devkit new NAME --profile native-ios --database postgres` | the option is `--set database=postgres` (there is no `--database` flag) |
| generated `ios/README.md` (native v0.1.0) | upgrade with `devkit upgrade-native` | the command is `devkit upgrade PROJECT --layer native` |
| `web-core-template/README.md` | "everything, 129 tests"; e2e "generates five apps" | 919 tests collected at v0.7.0 (32 `e2e`, 109 `db`) |
| `developer-platform/README.md` | "one of two repositories" | three repositories since v0.8.0 (the README's v0.8 paragraph is correct) |
| `developer-platform/docs/usage.md` (upgrade section) | range `>=0.1.0,<0.7.0 … at devkit 0.7.0` | devkit 0.8.0 supports `>=0.1.0,<0.8.0` (historical wording) |
| `developer-platform/docs/ci-evidence.md` | "Twenty-six tests … skip in CI" | 28 `integration`-marked tests at v0.8.0 (including the native pair tests) |
| `native-ios-template` scripts | – | `check-release-config.sh` writes `ios/.derived-data-release.log`, which no `.gitignore` covers, so a later upgrade sees an untracked file |
| `developer-platform/Brewfile` | Docker cask commented out | Docker is required by every database project and the e2e; `doctor` treats it as optional (warn) |

## Facts that could not be documented conclusively

- **Owner-reported troubleshooting items** (Homebrew architecture, Intel vs ARM, Node path, `-runFirstLaunch`, `DTServiceHubClient failed to bless service hub`, SpringBoard/PosterBoard): these are not recorded in any repository or in the acceptance evidence. Their entries give the toolchain's documented behaviour and safe recoveries, and are labelled *owner-reported*.
- **The exact Xcode version used by each acceptance run** is not recorded in the evidence TSVs; the acceptance workstation currently has Xcode 27.2, and the native template's CI uses the newest Xcode 26 on `macos-26`.
- **devkit 0.1.0** has no tag in the current repository (it predates the split); its contents are known only from `CHANGELOG.md`.
- **Hosted-test counting**: the acceptance run reports 11 hosted tests passing; in a normal `test.sh app` run, 3 of them (the end-to-end phases and marker) are disabled by `E2E_PHASE` and are counted by Swift Testing's summary.
- **Earlier work packages (WP1, WP2)** are not named in the repositories; only WP3 and WP4 are.
