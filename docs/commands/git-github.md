# Git, GitHub CLI and workflows

Git is not just storage here: a **clean, committed tree is the upgrade safety mechanism**, and **annotated release tags are the template versions**.

## Everyday Git

| Command | Purpose |
|---|---|
| `git switch -c feat/name` | Start work on a branch (never on `main`). |
| `git status` / `git status --porcelain -uall` | What `devkit upgrade` checks: must be empty. |
| `git diff` / `git diff --stat` | Review an upgrade or an agent's change. |
| `git add -A && git commit -m "type: summary"` | Conventional prefixes are used throughout (`feat:`, `fix:`, `chore:`, `docs:`). |
| `git stash -u` | Set aside work (including untracked files) before an upgrade. |
| `git restore --source=HEAD -- path` | Restore one file, for example an edited migration. |
| `git switch -` / `git switch main` | Leave an upgrade branch. |
| `git log --oneline -5` | Recent history. |
| `grep -rn '^<<<<<<< ' .` | Find conflict markers after an upgrade. |

!!! danger "Commands the platform forbids in its own code and docs"
    `git clean`, `git reset --hard`, forced pushes, `rm -rf`, `find … -delete`, recursive `chmod`/`chown`. A test in every repository fails if they appear in code, CI or documented snippets. Recover with branches, `git restore`, `git revert` and `git stash` instead. See [Recovery procedures](../upgrade/recovery.md).

## Release tags

Template and platform versions **are** annotated Git tags `vMAJOR.MINOR.PATCH`, created on a merge commit after CI passed on `main`.

```bash
git ls-remote --tags https://github.com/audiophreak/web-core-template.git    # what devkit reads
git tag -a v0.7.1 -m "web-core-template v0.7.1"
git push origin v0.7.1
git rev-parse v0.7.0^{commit}                                                 # the commit an annotated tag points at
```

Published tags are **never moved or deleted**; fix forward with a new patch release. `devkit` only considers tags that are exactly `vX.Y.Z`; pre-release and other tags are ignored.

## GitHub CLI

| Command | Purpose |
|---|---|
| `gh auth login` / `gh auth status` | Sign in; `doctor` checks status. Token scopes used: `repo`, `workflow`. |
| `gh auth setup-git` | Make `gh` Git's credential helper (private template access). |
| `gh repo clone audiophreak/<repo>` | Clone a repository (public or private). |
| `gh repo create NAME --private --source . --remote origin --push` | Publish a new generated project. |
| `gh repo view OWNER/NAME --json visibility` | Confirm a repository's visibility. |
| `gh pr create --fill` / `gh pr checks` / `gh pr view --web` | Pull requests. |
| `gh run list --commit SHA` / `gh run watch ID --exit-status` | Follow CI. |
| `gh run download ID --dir EMPTY_DIR` | Download CI evidence artifacts (`junit.xml`, `pytest-output.txt`, `metadata.txt`, `installed-packages.txt`). |
| `gh api repos/OWNER/REPO/git/ref/tags/vX.Y.Z` | Verify a published tag (then dereference the annotated tag object). |

## GitHub Actions workflows

| Repository | Workflow | Jobs |
|---|---|---|
| `developer-platform` | `.github/workflows/ci.yml` | `test` on ubuntu-latest, Python 3.12 and 3.14: `uv sync --locked`, `pytest` with JUnit evidence, token-shape scan, artifact upload (30 days) |
| `web-core-template` | `.github/workflows/ci.yml` | `test` (3.12, 3.14): `pytest -m "not db"` with full history and Node 26; `database`: `pytest -m db` with Docker required |
| `native-ios-template` | `.github/workflows/ci.yml` | `template` (ubuntu-24.04): `pytest -m "not xcode"`; `xcode` (macos-26, newest Xcode 26): render, static, contract, zero-diff regeneration, `swift test`, simulator app and package tests, Release https check, `pytest -m xcode` |
| generated project | `.github/workflows/ci.yml` | `check`: `npm ci` + `npm run check`; with a database, `database`: a `postgres:17.10` service, `npm run db:verify`, `npm run test:db` |
| this wiki | `.github/workflows/docs.yml` | build with `--strict`, link and diagram check |

Conventions: `permissions: contents: read`; `actions/checkout` with `persist-credentials: false`; actions pinned to full commit SHAs in the platform, web template and generated projects (the native template's workflow uses version tags, `@v4`/`@v6`); no repository secrets anywhere. See [GitHub CI versus local](../testing/ci.md).
