# Copier, Git and CI

## Copier upgrade conflicts

**Symptoms.** `devkit upgrade` exits **3**: `Upgraded to vX.Y.Z with merge conflicts in: <files>. Nothing was discarded …`. With raw `copier update`, exit 0 but `<<<<<<<` markers in files.

**Likely cause.** You and the template changed the same lines. Most common in `package.json`, `package-lock.json`, `src/app/globals.css`, `README.md`, `AGENTS.md`.

**Diagnostics.**

```bash
git status --short
grep -rln '^<<<<<<< ' --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=.derived-data .
git diff
```

**Safe recovery.** Edit each file, keeping both intents; for dependency files resolve `package.json` and then `npm install` (do not hand-merge the lock); `npm run check`; `git add -A && git commit`. To abandon: `git stash -u` (recoverable) and retry later.

**Evidence.** *Repository source* (`upgrade.py`, template `docs/upgrading.md`; a test confirms nothing is silently lost).

## Upgrade refused: dirty tree

**Symptoms.** `error: PROJECT has uncommitted changes (modified or untracked files). Commit or stash them first, so the upgrade can never mix with your work. Nothing was changed.` (exit 1). Or `… is not the root of a git repository`.

**Diagnostics.** `git status --porcelain -uall` (exactly what devkit runs).

**Safe recovery.** Commit or `git stash -u`. For build artifacts that should never be committed, add them to `.gitignore` (see [Recovery](../upgrade/recovery.md#the-clean-tree-requirement) for the known ones). For a project that is not a Git repository: `git init -b main && git add -A && git commit -m "chore: initial commit"`.

### Upgrade refused after running the iOS checks

**Status.** **Fixed in native-ios-template v0.1.1.** Affects only projects whose native layer is still v0.1.0.

**Symptom.** A clean tree becomes dirty after `sh ios/scripts/check-release-config.sh`: `?? ios/.derived-data-release.log`, and the next `devkit upgrade` exits 1 (`has uncommitted changes (modified or untracked files)`).

**Cause.** The v0.1.0 script wrote its build log to `ios/.derived-data-release.log`, which neither `ios/.gitignore` (it ignores `.derived-data/`) nor the root `.gitignore` covers. v0.1.1 writes the log to `ios/.derived-data/release.log`, inside the ignored build area, and still prints its last 30 lines (and names it) when the build fails.

**Recovery.** Move the stray log out of the project (`mv ios/.derived-data-release.log "$(mktemp -d)/"`), confirm `git status --porcelain` is empty, then upgrade the native layer to v0.1.1 ([procedure](../upgrade/layers.md#upgrading-a-v010-native-layer-to-v011)). Do not add the file to `.gitignore` by hand; the upgrade removes the cause.

**Evidence.** *Repository source* (native v0.1.1 `CHANGELOG.md`, `check-release-config.sh`, and the regression tests `tests/test_xcode.py`); *acceptance runs*: the v0.1.1 audit reproduced the defect on a v0.1.0 project (devkit upgrade refused, exit 1), upgraded it, and showed the tree stays clean afterwards.

## Upgrade refused: provenance

| Message | Cause | Recovery |
|---|---|---|
| `generated from commits after a release (vX.Y.Z-N-g…)` | rendered from an untagged template commit | regenerate from a release and move your code |
| `recorded template version '…' is not a release tag` | local-mode or hand-edited answers | regenerate, or restore the answers file from Git |
| `older than the oldest release this devkit supports` / `newer than this devkit supports` | devkit and project out of step | use a matching devkit (`git checkout vX.Y.Z` in the platform, `uv sync`) |
| `The project's template source is a local path` (warning) | generated with `--template PATH` | upgradable only from that checkout; not for sharing |
| `Release vX.Y.Z does not exist at …` | wrong `--to` or unreachable origin | `git ls-remote --tags <origin>` |

## Git state and recovery

| Situation | Non-destructive recovery |
|---|---|
| worked on `main` by mistake | `git switch -c feat/name` (carries uncommitted work); commit there |
| want to undo the last commit but keep the work | `git reset --soft HEAD~1` |
| want to undo a pushed commit | `git revert <sha>` |
| need to set work aside | `git stash -u`; later `git stash pop` |
| a file is wrong | `git restore --source=HEAD -- path` (or `--source=<sha>`) |
| detached HEAD after checking out a tag | `git switch -c inspect/v0.7.0` or `git switch main` |
| lost a commit | `git reflog`, then `git switch -c rescue <sha>` |

The platform bans `git reset --hard`, `git clean`, forced pushes and recursive deletes in its code and documentation, and AI agents working on it are told never to run them ([instructions](../ai-workflow/instructions.md#destructive-commands)).

## CI failures

| Symptom | Likely cause | Diagnose / fix |
|---|---|---|
| fails on Python 3.12 only | a newer-Python feature or stdlib behaviour | reproduce with `uv run --python 3.12 pytest`; fix forward |
| `The lockfile … needs to be updated` | `uv.lock` stale vs `pyproject.toml` | `uv lock` (with approval), commit |
| web template `database` job fails, `test` passes | Docker-only regression (`REQUIRE_DOCKER=1` makes missing Docker a failure) | `uv run pytest -m db` locally with Docker running |
| upgrade/byte-identity tests fail in CI only | shallow history (no tags) | the workflow uses `fetch-depth: 0`; keep it |
| native `xcode` job fails at "Select the newest installed Xcode 26" | runner image changed its Xcode set | read the step log (`ls /Applications/Xcode_26*`); adjust only with review |
| generated project CI: `format:check` fails on `.copier-answers.yml` | template < 0.3.0 rendered from an all-digit commit hash | fixed in 0.3.0 (`.prettierignore`); upgrade |
| `a token-shaped string was found in reports/` | a test printed something credential-shaped | find and stop the test from printing it; the match itself is never shown |
| `npm ci` fails in CI after an upgrade | `package.json` and lock disagree after a hand-resolved conflict | `npm install` locally, commit the lock |
| live gate tests "skipped" in platform CI | by design: no template checkout in CI | run `uv run pytest -m integration` locally |

Read the evidence: `gh run view <id> --log-failed`, `gh run download <id> --dir "$(mktemp -d)"`, then `junit.xml` and `metadata.txt` (`commit_under_test`). Never re-tag to "fix" a release; push a fix and tag a patch.
