# Compatibility and contract snapshots

## Release compatibility at the baseline

| devkit | Web Core releases supported | Native releases supported | Native ↔ web pairs |
|---|---|---|---|
| **v0.8.0** | `>=0.1.0,<0.8.0` (0.1.0 … 0.7.0) | `>=0.1.0,<0.2.0` (0.1.0) | native 0.1.x ↔ web `>=0.7.0,<0.8.0` |
| v0.7.0 | `>=0.1.0,<0.7.0` | – | – |
| v0.6.0 | `>=0.1.0,<0.6.0` | – | – |
| v0.5.0 | `>=0.1.0,<0.5.0` | – | – |
| v0.4.0 | `>=0.1.0,<0.4.0` | – | – |
| v0.3.0 | `>=0.1.0,<0.3.0` | – | – |
| v0.2.0 | `>=0.1.0,<0.2.0` | – | – |

An older devkit keeps working with the releases it knew and **never selects** a newer one. One devkit supports several template lines because each option declares `since`:

| Option | Refused for releases before |
|---|---|
| `zod` | 0.2.0 |
| `forms` | 0.3.0 |
| `rest_api` | 0.4.0 |
| `database` | 0.5.0 |
| `auth` | 0.6.0 |
| `native_client` | 0.7.0 |

This check exists because **Copier silently ignores an answer for a question that does not exist**: without it, `--template-ref v0.1.0 --set zod=true` would produce a project quietly without Zod. After generation, `devkit` also checks every requested option was recorded (a second line of defence against a wrong registry).

## Versioning rules

- Semantic versions; in 0.x a **minor** bump may break. Breaking for a template: a new Node major, a renamed or removed question, a changed type or default that alters existing projects.
- A breaking template release ships with a matching platform release (new range, new snapshot).
- New features default **off**, and the default output must be byte-identical to the previous tag apart from `.copier-answers.yml`.
- Tags are annotated, created on a merge commit after CI passed on `main`, and never moved or deleted. Fix forward.
- Order: **web template → native template (against the published web contract) → platform → published-pair acceptance.** The platform is never tagged before the template release it requires exists.

## Contract snapshots

```text
developer-platform/tests/contracts/
├── web-core/0.1.0.json … 0.7.0.json
└── native-ios/0.1.0.json
```

Each snapshot records what `devkit` depends on in one release: every `copier.yml` question with its type, default and choices, whether booleans are strict, and the Node major from `template/.nvmrc`. It is captured **from the release tag** with `git show REF:path`:

```bash
uv run python tools/capture_contract.py --template ../web-core-template --ref v0.7.0 --write
uv run python tools/capture_contract.py --kind native-ios --template ../native-ios-template --ref v0.1.0 --write
uv run python tools/capture_contract.py --template ../web-core-template --ref v0.7.0 --check
```

| Layer | Proves | Runs | Needs |
|---|---|---|---|
| **Offline snapshots** (`tests/test_contract_snapshots.py`) | For every supported release the registry agrees with its questions (types, defaults, choices, strictness, absence before `since`) and Node major; a snapshot exists for the oldest release and each release that introduced an option | CI and locally, always | nothing |
| **Live release gate** (`pytest -m integration`) | Each snapshot still equals the real template at its tag; old and new releases really generate with the right options; the native and web layers really share one API contract | before tagging, where the templates are checked out | the private checkouts |

**Why not check out the templates in platform CI?** It would need a stored credential able to read the private template repositories, usable by anyone who can change the workflow. Snapshots make it unnecessary; the live gate is run locally instead. Revisit if the repositories become public.

## The native contract

`native-ios-template/tools/web_contract.json` records the published web release and the SHA-256 of its `openapi/openapi.json`:

```json
{ "web_core_template_release": "v0.7.0",
  "sha256": "a42effbdb027d0c70efb669c8503ebb3fead0b8613f88e879114922274a9e82a" }
```

The acceptance run confirmed the generated web `openapi.json` and the iOS `Contract/openapi.json` are byte-identical (`a42effbdb027d0c7…`) for both database providers. A new web minor with API changes therefore needs a new native release before `devkit` will upgrade the web layer of a native project.

## Template provenance

`web-core-template/docs/provenance.md` records where the template came from: the reference Web Core application at its merged shadcn/ui baseline (commit `f244594`, merged as `bf3643c`). Rendering the template with the reference's name and comparing every file: 16 of 22 shared files byte-identical; the rest differ intentionally (exact pins instead of six `^` ranges, a description field, identity moved into `src/lib/app-info.json`, Copier's answers file). All 719 package-lock entries are identical apart from the project name and those six specifiers.
