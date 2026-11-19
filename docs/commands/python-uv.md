# uv, Python and pytest

Python is the platform and template-test language. Every Python repository (`developer-platform`, both templates, this wiki) uses uv with a committed `uv.lock`, exact pins, an `exclude-newer` cutoff and `python-downloads = "never"`.

## uv

| Command | Purpose | Notes |
|---|---|---|
| `uv sync` | Create/refresh `.venv` from `uv.lock` | Run after cloning and after pulling a lock change. |
| `uv sync --locked` | Same, but fail if `uv.lock` is out of date with `pyproject.toml` | What CI runs. Prefer it. |
| `uv run CMD` | Run inside the project environment | `uv run devkit …`, `uv run pytest`, `uv run copier …`. |
| `uv run --locked CMD` | Run, refusing a stale lock | CI form. |
| `uv run --project PATH devkit …` | Run `devkit` from anywhere | Useful inside a generated project. |
| `uv pip freeze --exclude-editable` | List installed versions | CI evidence. |

**The supply-chain rule.** `[tool.uv] exclude-newer` (2026-11-02 in the platform and web template, 2026-11-04 in the native template) means uv resolves only packages published before that date: a rolling two-week buffer, raised deliberately when upgrading dependencies.

**Failure modes.** `The lockfile needs to be updated` with `--locked`: someone changed `pyproject.toml` without relocking (`uv lock`, with approval). `No interpreter found`: install Homebrew `python@3.14`; uv will not download one.

## pytest

| Repository | Command | What runs | Count at the baseline |
|---|---|---|---|
| `developer-platform` | `uv run pytest` | Unit, safety, offline contract snapshots, fixture-template integration; live gate skips without checkouts | 503 collected |
| | `uv run pytest -m integration` | Live release gate against `../web-core-template` and `../native-ios-template` (or `$WEB_CORE_TEMPLATE`) | 28 |
| `web-core-template` | `uv run pytest -m "not e2e"` | Fast: render, validators, versions, upgrades, lock matrix | – |
| | `uv run pytest -m e2e` | Generate apps, `npm ci` + `npm run check` in each (needs Node 26, network) | 32 |
| | `uv run pytest -m db` | Real PostgreSQL and Supabase in Docker (needs a running daemon) | 109 |
| | `uv run pytest` | Everything | 919 collected |
| `native-ios-template` | `uv run pytest -m "not xcode"` | Rendering, layering, static rules, pins, update, documented devkit commands | 51 |
| | `uv run pytest -m xcode` | Generated client, `swift test`, `xcodebuild` on a simulator, the Release check leaves the tree clean | 7 |

Counts are collected tests at the release tags (`pytest --collect-only`); markers overlap slightly in the web template.

Useful options:

```bash
uv run pytest -q -rfEs                      # quiet, with a summary of failures, errors and skips
uv run pytest tests/test_upgrade.py -k sticky
uv run pytest -x                            # stop at the first failure
```

**Failure modes.** A test in each repository fails if code, CI or documented shell snippets contain recursive deletes, `git clean`, `git reset --hard` or forced pushes (`test_no_destructive_commands.py`); that is intentional. `-m db` tests **fail** rather than skip in CI when Docker is missing (`REQUIRE_DOCKER=1`).

## Platform maintenance tools

```bash
uv run python tools/scratch.py new                      # a fresh, marked workspace under the temp dir
uv run python tools/scratch.py clean WORKSPACE [CHILD]  # the only sanctioned delete
uv run python tools/capture_contract.py --template ../web-core-template --ref v0.7.0 --check
uv run python tools/capture_contract.py --kind native-ios --template ../native-ios-template --ref v0.1.0 --check
```

`scratch.py clean` refuses symlinks, `..` escapes, `/`, the home directory, the current directory and anything not inside a workspace it created.

## Template maintenance tools

```bash
# web-core-template
uv run python tools/refresh_locks.py --check     # every locks/<key>.json still derives from locks/base.json
uv run python tools/compare_release.py v0.6.1    # default output byte-identical to the previous release
# native-ios-template
uv run python tools/gen_pbxproj.py --check       # the committed Xcode project equals the generator's output
```
