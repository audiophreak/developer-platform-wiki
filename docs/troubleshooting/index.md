# How to diagnose

Every entry in this section has the same shape: **symptoms**, **likely cause**, **diagnostic commands**, **safe recovery**, and **evidence** (where the problem is recorded). Evidence labels:

| Label | Meaning |
|---|---|
| *Repository source* | the behaviour or fix is in the released code, scripts, tests or docs |
| *Acceptance runs* | observed in the published-pair acceptance evidence (three recorded runs) |
| *Owner-reported* | encountered during development and reported by the owner; not recorded in the repositories, so the diagnosis is based on the toolchain's documented behaviour |

## First moves

```bash
uv run --project ~/Developer/developer-platform devkit doctor    # workstation, read-only
git status --short && git log --oneline -3                        # where am I
uv run --project ~/Developer/developer-platform devkit status .   # template layers
npm run db:status                                                 # database, if any
```

Then read the exact error text. The platform's messages say what to do; most of this section expands on them.

## Index

| Symptom (abridged) | Page |
|---|---|
| `brew` installs x86_64 binaries; tools in `/usr/local` | [Workstation](workstation.md#homebrew-architecture-and-path) |
| `Bad CPU type in executable`, Rosetta prompts, slow Docker images | [Workstation](workstation.md#intel-versus-arm-binaries) |
| `doctor`: `node … generated projects pin 26.x`; `npm ci` engine errors | [Workstation](workstation.md#node-and-npm-path-issues) |
| `Template source is unavailable` | [Workstation](workstation.md#private-template-access) |
| Xcode too old; `xcodebuild` license or first-launch errors | [Xcode](xcode.md#xcode-version-compatibility) |
| no iOS runtime; `no iPhone simulator is installed` | [Xcode](xcode.md#simulator-runtime-management) |
| `The test runner hung before establishing connection` | [Xcode](xcode.md#xctest-runner-hangs) |
| `DTServiceHubClient failed to bless service hub` | [Xcode](xcode.md#dtservicehubclient-failed-to-bless-service-hub) |
| SpringBoard / PosterBoard crashes, simulator never finishes booting | [Xcode](xcode.md#simulator-springboard-and-posterboard-failures) |
| Keychain `-34018` | [Xcode](xcode.md#keychain-error-34018) |
| `cannot connect to the database (28P01)` after a fresh `db:init` | [Database](database.md#stale-docker-volumes-and-28p01) |
| `password authentication failed for user "app_runtime"` | [Database](database.md#postgresql-authentication-failures) |
| Supabase stack stopped by `db:up`; port conflicts; `.temp` dirty tree | [Database](database.md#supabase-lifecycle-issues) |
| `exit 3` with conflict markers | [Copier, Git, CI](git-copier-ci.md#copier-upgrade-conflicts) |
| `has uncommitted changes (modified or untracked files)` | [Copier, Git, CI](git-copier-ci.md#upgrade-refused-dirty-tree) |
| red CI on a PR | [Copier, Git, CI](git-copier-ci.md#ci-failures) |
