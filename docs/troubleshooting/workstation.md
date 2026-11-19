# Workstation and toolchains

## Homebrew architecture and path

**Symptoms.** `brew --prefix` prints `/usr/local` on an Apple-silicon Mac; tools installed by `brew bundle` are not the ones `which` finds; `brew` warns about running under Rosetta; two copies of `git`, `python3` or `uv` exist.

**Likely cause.** An Intel (x86_64) Homebrew in `/usr/local` alongside, or instead of, the native arm64 Homebrew in `/opt/homebrew`, often from a migrated machine or a terminal running under Rosetta. Whichever `brew shellenv` runs last in your shell profile wins `PATH`.

**Diagnostics.**

```bash
uname -m                                   # arm64 expected (x86_64 = this shell runs under Rosetta)
sysctl -n sysctl.proc_translated 2>/dev/null   # 1 = translated by Rosetta
brew --prefix                              # /opt/homebrew expected
which -a brew git python3 uv gh fnm        # every copy on PATH, in order
file "$(command -v git)"                   # Mach-O 64-bit executable arm64
grep -n 'brew shellenv' ~/.zprofile ~/.zshrc 2>/dev/null
```

**Safe recovery.** Make `/opt/homebrew/bin` first: `eval "$(/opt/homebrew/bin/brew shellenv)"` in `~/.zprofile`, and remove any `/usr/local/bin/brew shellenv` line. Open a new terminal (not "Open using Rosetta"). Re-run `brew bundle --file=Brewfile` with the arm64 `brew`, then `devkit doctor`. Uninstalling the Intel Homebrew is optional and a separate, deliberate decision.

**Evidence.** *Owner-reported.* The acceptance workstation is arm64 with Homebrew in `/opt/homebrew`.

## Intel versus ARM binaries

**Symptoms.** `Bad CPU type in executable`; a tool works in one terminal and not another; Docker warns `The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64)`; very slow containers; native Node modules or Swift builds fail with architecture mismatches.

**Likely cause.** An x86_64 binary (Intel Homebrew, an Intel Node download, a terminal under Rosetta) mixed with arm64 tools, or an amd64-only container image.

**Diagnostics.**

```bash
file "$(command -v node)" "$(command -v python3)" "$(command -v uv)"
node -p 'process.arch'                     # arm64
python3 -c 'import platform; print(platform.machine())'
docker version --format '{{.Server.Arch}}'
docker image inspect postgres:17.10 --format '{{.Architecture}}'
```

**Safe recovery.** Use arm64 builds throughout: Homebrew in `/opt/homebrew`, Node installed by fnm from an arm64 shell, uv's interpreter from Homebrew's `python@3.14`. The generated `compose.yaml` pins `postgres:17.10` by its **multi-arch index digest**, so Docker pulls the native arm64 image; do not replace it with a single-arch digest. After fixing Node, `npm ci` again (reinstalls native modules for the right architecture).

**Evidence.** *Owner-reported*; the multi-arch digest is *repository source* (`compose.yaml`, `docs/features.md`).

## Node and npm path issues

**Symptoms.** `devkit doctor`: `[FAIL] node 25.x; generated projects pin 26.x` (or `not found on PATH`); `npm ci` prints `EBADENGINE` for `"node": ">=26 <27"`; `npm run check` works in one terminal only; CI passes but local fails.

**Likely cause.** fnm's shell hook is not loaded, so a system or Homebrew `node` comes first on `PATH`; or the project's `.nvmrc` (`26`) is not selected automatically on `cd`; or a global Node from another installer shadows fnm.

**Diagnostics.**

```bash
which -a node npm
node --version && npm --version            # v26.x / 11.x
fnm list && fnm current
cat .nvmrc                                 # 26
echo "$PATH" | tr ':' '\n' | head
```

**Safe recovery.**

```bash
fnm install 26 && fnm default 26
echo 'eval "$(fnm env --use-on-cd)"' >> ~/.zshrc     # then open a new terminal
cd PROJECT && node --version                         # v26.x
npm ci
```

If a Homebrew `node` formula is installed it can shadow fnm; fnm's hook prepends its directory, so loading the hook last in `~/.zshrc` is enough. Never "fix" an engine error by editing `engines`; the upper bound is deliberate.

**Evidence.** *Owner-reported*; the `doctor` check and `engines` range are *repository source*. On the acceptance workstation `node` resolves to fnm's per-shell directory, ahead of everything else on `PATH`.

## Private template access

**Symptoms.** `Template source is unavailable: https://github.com/audiophreak/web-core-template.git (…). Check the address. If the repository is private, git must be able to authenticate without prompting …`; `doctor` warns `no credential helper configured`.

**Likely cause.** Git has no non-interactive credentials for `github.com` (`devkit` sets `GIT_TERMINAL_PROMPT=0`, so Git cannot ask), `gh` is logged out, or the token lacks `repo` scope.

**Diagnostics.**

```bash
gh auth status
git config --get-regexp '^credential\..*helper$'
GIT_TERMINAL_PROMPT=0 git ls-remote --tags https://github.com/audiophreak/web-core-template.git | tail -3
```

**Safe recovery.** `gh auth login` (scopes `repo`, `workflow`), then `gh auth setup-git`; or the one-command `gh_git` wrapper from [setup](../getting-started/setup.md#private-repository-access). Retry.

**Evidence.** *Repository source* (`sources.py`, `docs/publishing.md`).

## Python and uv

| Symptom | Cause | Fix |
|---|---|---|
| `No interpreter found for Python >=3.12` | uv may not download Python (`python-downloads = "never"`) | `brew install python@3.14` |
| `The lockfile at uv.lock needs to be updated` | `pyproject.toml` changed without a relock | discard the unapproved change, or `uv lock` with approval |
| `Cannot find the developer-platform checkout (Brewfile and src/devkit)` | `devkit` run outside a checkout | `uv run --project ~/Developer/developer-platform devkit …` |
