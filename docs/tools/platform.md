# Platform and generation tools

## Homebrew and the Brewfile

| | |
|---|---|
| **Problem** | Installing the same workstation tools reproducibly on macOS. |
| **Why selected** | The standard macOS package manager; `brew bundle check` gives a read-only "is everything installed" answer. |
| **Invoked by** | You (`brew bundle --file=Brewfile`); `devkit doctor` runs `brew bundle check`. |
| **Consumes / produces** | `developer-platform/Brewfile` → binaries in `/opt/homebrew`. |
| **Depended on by** | git, gh, uv, python@3.14, fnm. |
| **Phase** | Workstation. |
| **Caveats** | `devkit` never installs. Docker is a commented-out cask: install a Docker runtime yourself. On Apple silicon use the arm64 Homebrew in `/opt/homebrew`, not an Intel one in `/usr/local`. |

## uv

| | |
|---|---|
| **Problem** | Reproducible, project-local Python environments without global installs. |
| **Why selected** | Fast, lockfile-based (`uv.lock`), supports `exclude-newer` (the two-week supply-chain buffer) and `python-downloads = "never"`. |
| **Invoked by** | You (`uv sync`, `uv run …`), every CI workflow (`pip install uv==0.13.6`). |
| **Consumes / produces** | `pyproject.toml` + `uv.lock` → `.venv/`. |
| **Depended on by** | devkit, Copier, pytest, the templates' test suites, this wiki's Zensical. |
| **Phase** | Workstation, generation, CI. |
| **Caveats** | `--locked` fails on a stale lock; uv will not download an interpreter, so a missing Python must be installed with Homebrew. |

## Python

| | |
|---|---|
| **Problem** | A language for the CLI and for template tests that drive Copier, npm, Docker and Xcode as subprocesses. |
| **Why selected** | Copier is Python; one language for the platform, its tests and the templates' tests. |
| **Invoked by** | uv. |
| **Phase** | Generation, CI. |
| **Caveats** | Floor 3.12 (`requires-python`); CI tests 3.12 and 3.14. |

## Copier

| | |
|---|---|
| **Problem** | Parameterized project templates that can **upgrade** existing projects, not just create them. |
| **Why selected** | Versioned templates via Git tags, `copier update` with a three-way merge, multiple answers files per project (layering), and a Python API. Alternatives rejected in `developer-platform/docs/architecture.md`: `create-next-app` + scripts, Cookiecutter, GitHub template repositories (no upgrades or parameters), Yeoman/Plop (JavaScript tooling), Nx/Turborepo generators (assume a monorepo). |
| **Invoked by** | `devkit` (`run_copy`, `run_update`); you, for template development. |
| **Consumes** | A template repository at a Git ref: `copier.yml` (questions, validators), `template/` (files, `.jinja` suffix for substituted ones), `locks/` (included by a Jinja shim). |
| **Produces** | Rendered files and an answers file (`_src_path`, `_commit`, answers). |
| **Depended on by** | Every generated project's provenance and upgrade path. |
| **Phase** | Generation. |
| **Caveats** | `type: bool` answers are cast before validators run (hence the strict-boolean pattern); raw `update` takes the newest tag without `--vcs-ref`, exits 0 on conflicts and cannot see a previous answer; Jinja inside JSON/TSX/YAML needs care; lockfiles do not compose (hence the lock matrix). Its `Worker` internals are not a public API, so `devkit` uses only `run_copy`/`run_update`. |

## devkit

| | |
|---|---|
| **Problem** | Make generation and upgrades safe and repeatable: only supported releases, explicit choices, no overwrites, nothing hidden. |
| **Why selected** | A thin, tested wrapper owns the policy (which releases, which options, which profiles) while the templates own content. |
| **Invoked by** | You or an AI agent: `uv run devkit doctor|new|status|upgrade|native add`. |
| **Consumes** | The profile registry (`src/devkit/profiles.py`), remote release tags, CLI arguments, a project's answers files. |
| **Produces** | Projects (via Copier), upgrade plans, status reports; exit codes 0/1/2/3. |
| **Depended on by** | The normal workflow; the acceptance audit. |
| **Phase** | Workstation (doctor), generation, upgrade. |
| **Caveats** | Runs only from a checkout (it finds its `Brewfile`); needs non-interactive Git credentials; never commits. Details: [developer-platform architecture](../architecture/developer-platform.md). |

## pytest

| | |
|---|---|
| **Problem** | One test runner for unit tests, template rendering, real npm builds, real databases and Xcode builds. |
| **Why selected** | Standard Python runner; markers (`integration`, `e2e`, `db`, `xcode`) separate slow or environment-dependent suites. |
| **Invoked by** | You, CI (with JUnit XML evidence), the release gates. |
| **Phase** | CI, release. |
| **Caveats** | `tmp_path_retention_policy = "failed"` keeps only failing tests' temporary directories (an e2e app is hundreds of MB). |

## Platform maintenance scripts

| Tool | Repository | Purpose |
|---|---|---|
| `tools/scratch.py` | developer-platform | disposable workspaces; the only sanctioned way to delete |
| `tools/capture_contract.py` | developer-platform | capture/verify a template release's question contract snapshot |
| `tools/features.py` | web-core-template | enumerate the supported feature matrix from `features.yml` |
| `tools/refresh_locks.py` | web-core-template | derive feature lockfiles from `locks/base.json`, strictly additively |
| `tools/compare_release.py` | web-core-template | prove default output is byte-identical to a previous tag |
| `tools/gen_pbxproj.py` | native-ios-template | generate the static Xcode project; `--check` for drift |
