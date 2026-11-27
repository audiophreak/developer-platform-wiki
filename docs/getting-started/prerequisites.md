# Prerequisites

Everything below is checked, read-only, by `devkit doctor` ([setup](setup.md)). Nothing in the platform installs software for you: that is a deliberate rule (`developer-platform/AGENTS.md`: "Never run anything that installs software globally or changes workstation configuration").

## Summary

| Tool | Required for | Version at the baseline | `doctor` check |
|---|---|---|---|
| macOS on Apple silicon | everything native; recommended overall | macOS 27 on arm64 in the acceptance workstation | `platform` |
| Homebrew | installing the `Brewfile` | any current | `brew`, `brewfile` (warn) |
| Git | everything | ≥ 2.27 (Copier's floor) | `git` (fail), `git identity` (warn) |
| GitHub CLI `gh` | repositories, private template access | current | `gh`, `gh auth` (warn) |
| uv | Python environments | CI pins 0.13.6 | `uv` (fail) |
| Python | `devkit`, Copier, template tests | ≥ 3.12 (CI tests 3.12 and 3.14) | `python` (fail) |
| fnm (or nvm/mise) | selecting Node per project | current | `fnm` (warn) |
| Node.js + npm | every generated web project | Node **26.x** (`.nvmrc` = `26`, `engines` `>=26 <27`); npm 11 | `node`, `npm` (fail) |
| Docker | `database=postgres` / `supabase`, `test:db`, e2e | Docker Desktop or OrbStack | `docker` (warn) |
| Supabase CLI | `database=supabase` only | **2.122.1**, an npm dev dependency of the project; no global install | not checked |
| Xcode | `native-ios` profile | **26 or newer** (iOS 17.0 deployment target) | `xcode` (warn) |
| iOS Simulator runtime | native tests and e2e | any iOS runtime | `ios simulator` (warn) |
| Claude Code | AI-assisted work | current | not checked |

"fail" checks make `devkit doctor` exit 1. "warn" checks never fail it, because only some profiles need them.

## 1. Homebrew and the Brewfile

The platform's `Brewfile` lists the workstation tools:

```ruby title="developer-platform/Brewfile"
brew "git"
brew "gh"
brew "uv"
brew "python@3.14"
brew "fnm"
# cask "docker-desktop"   (commented: install a Docker runtime yourself)
```

Install it yourself, once you have cloned the platform ([setup](setup.md)):

```bash
brew bundle --file=Brewfile
brew bundle check --verbose --file=Brewfile   # what doctor runs, read-only
```

!!! warning "Apple silicon: use the native Homebrew"
    On Apple silicon Homebrew lives in `/opt/homebrew`; an Intel (Rosetta) Homebrew lives in `/usr/local`. Mixing them gives you x86_64 binaries on an arm64 machine and confusing PATH order. Check with `uname -m` (expect `arm64`) and `brew --prefix` (expect `/opt/homebrew`). See [Workstation troubleshooting](../troubleshooting/workstation.md#homebrew-architecture-and-path).

Node is deliberately **not** in the Brewfile: each project pins its own major in `.nvmrc`, and a version manager selects it.

## 2. Python and uv

`uv` creates a project-local `.venv` from each repository's `uv.lock`. Nothing is installed globally, and every repository sets `python-downloads = "never"`, so uv uses an interpreter already on the machine (Homebrew's `python@3.14`) rather than downloading one.

```bash
uv --version
python3 --version      # 3.12 or newer
```

## 3. Node.js and npm (via fnm)

```bash
fnm install 26
fnm default 26
eval "$(fnm env --use-on-cd)"   # add to ~/.zshrc so `cd` into a project selects its .nvmrc
node --version                   # v26.x
npm --version                    # 11.x
```

Every generated project contains `.nvmrc` with `26` and `"engines": { "node": ">=26 <27" }`. The upper bound is deliberate: dependency pins were verified on Node 26, and a new major is a reviewed template release.

## 4. Docker

Needed by every project with a database, by `npm run test:db`, by the template's `db` tests and by the native end-to-end scenario. Docker Desktop or OrbStack both work; the generated `compose.yaml` pins `postgres:17.10` by its multi-architecture digest, so Apple silicon and Linux pull the same release.

```bash
docker --version
docker info > /dev/null && echo "daemon reachable"
```

## 5. Supabase CLI

Not a workstation install. A project generated with `database=supabase` has `supabase` **2.122.1** as an exact-pinned npm dev dependency, so `npm ci` installs it and the project's scripts call it with `npx --no-install supabase`. Running `npx supabase` outside such a project fails by design.

## 6. Xcode and the iOS Simulator

Only for the `native-ios` profile.

```bash
xcodebuild -version                 # 26 or newer
xcode-select -p                     # /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch     # once after installing or updating Xcode
xcrun simctl list runtimes          # at least one "iOS ..." runtime
```

Install a Simulator runtime from **Xcode › Settings › Components** if none is listed. No Apple developer account, team or signing identity is needed: everything builds and tests on the simulator unsigned. See [Xcode and the Simulator](../troubleshooting/xcode.md) for first-launch and runtime problems.

## 7. Git and GitHub

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@users.noreply.github.com"
gh auth login                      # scopes used by the platform: repo, workflow
gh auth setup-git                  # lets git (and so Copier) read a private template without prompting
```

If a template repository is **private**, Git needs credentials. `devkit` runs Git with prompting disabled (`GIT_TERMINAL_PROMPT=0`) and never touches credentials, so Git must already be able to authenticate non-interactively. `gh auth setup-git` is the recommended way; [setup](setup.md#private-repository-access) lists the alternatives.

## 8. Claude Code

Install Claude Code and sign in. Every repository and every generated project carries `AGENTS.md` (the rules) and a one-line `CLAUDE.md` that imports it, so Claude Code picks up the rules automatically. See [AI-Assisted Development](../ai-workflow/index.md).
