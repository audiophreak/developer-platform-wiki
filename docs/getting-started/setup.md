# Repositories and setup

## The repositories

| Repository | Role | You normally |
|---|---|---|
| `audiophreak/developer-platform` | The `devkit` CLI, `Brewfile`, `doctor`, the profile registry, contract snapshots, platform docs | clone once, run `devkit` from it |
| `audiophreak/web-core-template` | The Web Core Copier template (`copier.yml`, `template/`, `locks/`, `features.yml`) and its tests | clone only to develop the template |
| `audiophreak/native-ios-template` | The native iOS add-on Copier template (owns `ios/` only) and its tests | clone only to develop the template |
| `audiophreak/developer-platform-wiki` | This manual | clone to read or edit it |
| your applications | Generated repositories; each is independent after generation | create with `devkit new` |

All five are private. `devkit new` reads the templates **from GitHub at a release tag**, so you do not need the template checkouts to generate projects. You need them to develop the templates or to run the platform's live release gate.

## Conventional layout

The repositories' docs and tests assume the checkouts are siblings:

```text
~/Developer/
├── developer-platform/        # devkit; tests look for ../web-core-template and ../native-ios-template
├── web-core-template/
├── native-ios-template/
├── developer-platform-wiki/
└── my-app/                    # generated projects can live anywhere outside the checkouts
```

`devkit new` refuses a destination inside the `developer-platform` checkout or inside a local template checkout it is rendering, so generated projects always live outside them.

## Clone and set up the platform

```bash
mkdir -p ~/Developer && cd ~/Developer
gh repo clone audiophreak/developer-platform
cd developer-platform
git checkout v0.8.1            # optional: pin exactly the accepted release
uv sync --locked               # .venv from uv.lock: copier 9.19.1, pytest 9.2.0, devkit itself
uv run devkit --version        # devkit 0.8.1
uv run devkit doctor
```

`devkit` is not installed globally. It runs from the checkout because it finds its own `Brewfile` by walking up from its source file; `uv run devkit` is the supported invocation.

## `devkit doctor`

Read-only. It runs version queries, `git config --get`, `gh auth status`, `xcodebuild -version`, `xcrun simctl list runtimes` and `brew bundle check`, parses only versions and exit codes, and never prints identities or tokens. A healthy workstation at the baseline looks like this:

```text
[ok  ] platform         darwin
[ok  ] python           3.14.10 (need >= 3.12)
[ok  ] copier           9.19.1 (project-local)
[ok  ] git              2.56.1 (need >= 2.27)
[ok  ] git identity     user.name and user.email are configured
[ok  ] node             26.13.1 (generated projects pin 26.x)
[ok  ] npm              11.20.0
[ok  ] uv               0.13.8
[ok  ] gh               2.104.0
[ok  ] gh auth          authenticated
[ok  ] git credentials  a credential helper is configured (private repositories)
[ok  ] brew             found
[ok  ] fnm              found
[ok  ] docker           found
[warn] mise             not found (evaluated, not required)
[ok  ] xcode            27.2 (the native-ios profile needs 26+)
[ok  ] ios simulator    an iOS runtime is installed
[ok  ] brewfile         all Brewfile entries are installed

All required checks passed (1 warning(s)).
```

Exit code `0` means no required check failed; warnings never fail it. The `mise` warning is expected: mise was evaluated and not adopted.

## Private repository access

Anything that reads a template needs Git credentials that work **without a prompt**: `devkit new`, `devkit upgrade`, `devkit status` (it lists remote tags), `devkit native add`, and raw `copier copy`/`copier update`. Choose one:

=== "gh as credential helper (recommended)"

    ```bash
    gh auth setup-git
    ```

    Adds `gh` as Git's credential helper for `github.com` in your global Git configuration; the token stays in the system keyring.

=== "macOS Keychain"

    Use Git's `osxkeychain` helper with a fine-grained personal access token that can read the template repositories. Git prompts once and stores it.

=== "One command, no configuration change"

    From `developer-platform/docs/publishing.md`: the token goes from the `gh` keyring to Git over stdin, never into arguments or logs.

    ```bash
    gh_git() {
      GIT_CONFIG_COUNT=2 \
      GIT_CONFIG_KEY_0='credential.https://github.com.helper' GIT_CONFIG_VALUE_0='' \
      GIT_CONFIG_KEY_1='credential.https://github.com.helper' GIT_CONFIG_VALUE_1='!gh auth git-credential' \
      "$@"
    }
    gh_git uv run devkit new my-app --output-dir ..
    ```

    Set it before the process starts: Copier's Git library reads the environment at start-up.

Without access, `devkit new` stops with `Template source is unavailable: ... If the repository is private, git must be able to authenticate without prompting`.

## Optional: the template checkouts

Only for template development or the platform's live release gate:

```bash
cd ~/Developer
gh repo clone audiophreak/web-core-template
gh repo clone audiophreak/native-ios-template
(cd web-core-template && uv sync --locked)
(cd native-ios-template && uv sync --locked)
```

## Optional: this manual

```bash
cd ~/Developer
gh repo clone audiophreak/developer-platform-wiki
cd developer-platform-wiki && uv sync --locked && uv run zensical serve --open
```
