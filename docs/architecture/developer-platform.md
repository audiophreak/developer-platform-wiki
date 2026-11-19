# developer-platform (devkit)

## Layout

```text
developer-platform/
├── Brewfile                  # checked by doctor, installed by you
├── pyproject.toml uv.lock    # devkit 0.8.0, copier==9.19.1, pytest==9.2.0 (dev), exclude-newer
├── src/devkit/
│   ├── cli.py                # argparse: doctor, new, upgrade, status, native add; exit codes
│   ├── doctor.py             # read-only checks
│   ├── profiles.py           # THE CONTRACT: profiles, TemplateSpec, Option, ranges, NATIVE_REQUIRES_WEB
│   ├── sources.py            # published vs local mode, release tag resolution (git ls-remote)
│   ├── validation.py         # safe path segment, --set parsing, `since` gate
│   ├── generate.py           # devkit new: profile rules, staging, run_copy, native layer, verification
│   ├── upgrade.py            # devkit upgrade: clean tree, range, sticky, pair rule, run_update, conflicts
│   ├── layers.py             # devkit native add, devkit status
│   ├── gitutil.py            # non-interactive git, URL credential redaction
│   ├── errors.py             # DevkitError → exit 1, UsageError → 2, UpgradeConflictError → 3
│   └── paths.py              # find the checkout (Brewfile + src/devkit)
├── tools/                    # scratch.py, capture_contract.py
├── tests/                    # 503 tests; contracts/web-core/0.1.0…0.7.0.json, contracts/native-ios/0.1.0.json
└── docs/                     # architecture, usage, publishing, release strategy, milestone reports, NEXT_SESSION
```

## The registry (`profiles.py`)

A `TemplateSpec` per template:

| Field | Web Core | Native iOS |
|---|---|---|
| `url` | `https://github.com/audiophreak/web-core-template.git` | `https://github.com/audiophreak/native-ios-template.git` |
| `versions` | `>=0.1.0,<0.8.0` | `>=0.1.0,<0.2.0` |
| `node_major` | `26` | `0` (not a Node template) |
| `answers_file` | `.copier-answers.yml` | `.copier-answers.ios.yml` |
| `options` | `cache_components`, `zod`, `forms`, `rest_api`, `database`, `auth`, `native_client` | `app_display_name`, `bundle_identifier`, `debug_api_port`, `release_api_host` |

Each `Option` has a `kind` (`bool`, `str`, `int`), the template's `default` (a contract test keeps them equal), `since` (first release that has it), optional `choices`, and `sticky` with a `sticky_reason`.

A `Profile` combines a template with `fixed` options (part of what the profile *is*) and `required` options (architectural choices the person must state), and optionally a `native` second template.

```python
NATIVE_REQUIRES_WEB = { (0, 1): VersionRange((0, 7, 0), (0, 8, 0)) }   # native 0.1.x ↔ web 0.7.x
```

## Source resolution (`sources.py`)

| Mode | Trigger | Renders | Records in the project |
|---|---|---|---|
| **published** (default) | no `--template`, or `--template URL`, or a bare repository path | the newest `vX.Y.Z` tag inside the range, or `--template-ref` (must be a supported release that exists) | the URL and the tag |
| **local** | `--template PATH` to a checkout | the working tree as on disk (`HEAD` ref, uncommitted edits included), or any `--template-ref` | a home-relative path `~/…`; warns it is not shareable |

Only plain `vMAJOR.MINOR.PATCH` tags count. Branches and untagged commits are never rendered in published mode.

## Principles enforced in code

| Principle | Where |
|---|---|
| Cheap checks first; nothing touches the network or disk on bad input | `generate.generate_project`, `upgrade.plan_upgrade` |
| Never overwrite: any existing path at the destination is refused; destinations inside a checkout are refused | `generate.resolve_destination`, `_ensure_outside` |
| Never pick an architecture | `apply_profile_options` (`required=("database",)`) |
| Never switch a feature on for you | rules live in the template's validators; `native add` refuses when `native_client` is off |
| Defence in depth: verify each requested option was recorded | `verify_options_recorded` |
| Never guess in a two-layer project | `_resolve_layer` refuses `--layer auto` there |
| Never mix with uncommitted work | `_clean_repository` (`git status --porcelain -uall` must be empty) |
| Never handle credentials | `gitutil.git` (`GIT_TERMINAL_PROMPT=0`), `redact()` |
| No code execution from templates | `unsafe=False`, `Settings()` |

## Release discipline for the registry

From `AGENTS.md`: a template release that changes the contract (Node major, questions) needs a matching registry change (range, `node_major`, options with `since`), a **new contract snapshot captured from the release tag**, and a passing live release gate (`pytest -m integration`). The platform is tagged only after the template release it requires exists.
