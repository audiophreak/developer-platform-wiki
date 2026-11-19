# devkit

`devkit` is the platform's Python CLI (`developer-platform/src/devkit/`, `argparse`). It checks the workstation, generates projects from the profile's templates at a supported release, and upgrades them. It is run from the checkout:

```bash
cd ~/Developer/developer-platform
uv run devkit --version          # devkit 0.8.0
uv run devkit COMMAND --help
```

Global guarantees (from `AGENTS.md` and the code): it never installs software, never prompts for or stores credentials (Git runs with `GIT_TERMINAL_PROMPT=0`; URL credentials are redacted from messages), never overwrites a destination, never deletes, and never commits.

---

## devkit doctor

**Purpose.** Read-only workstation check. **Usage.** `uv run devkit doctor`. **No options.**

Checks: platform; Python ≥ 3.12; Copier (project-local); Git ≥ 2.27 and identity; Node major equal to the Web Core profile's `node_major` (26) and npm; uv; `gh` and `gh auth status`; whether any Git credential helper is configured; optional `brew`, `fnm`, `docker`, `mise`; Xcode ≥ 26 and an iOS Simulator runtime (warnings only); `brew bundle check` against the `Brewfile`.

**Where it fits.** First thing on a new machine; again after upgrading Xcode, Node or Homebrew.

**Failure modes.** Exit 1 if any *required* check fails (Python, Copier, Git, Node, npm, uv). A `node … generated projects pin 26.x` failure means the wrong Node is first on `PATH`: `fnm use 26`. A `git credentials` warning means private-template access will fail.

---

## devkit new

**Purpose.** Create `OUTPUT_DIR/NAME` from the profile's template(s) at the newest supported release.

```bash
uv run devkit new NAME [--description TEXT] [--output-dir DIR] [--profile web-core|full-stack|native-ios]
                       [--set NAME=VALUE ...] [--template PATH_OR_URL] [--template-ref REF]
                       [--native-template PATH_OR_URL] [--native-template-ref REF] [--native-set NAME=VALUE ...]
                       [--dry-run]
```

| Option | Meaning |
|---|---|
| `NAME` | Directory and app name. The template validates the format (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`, ≤ 64). |
| `--description` | One line; template default `A Next.js application`. |
| `--output-dir` | Existing directory to create `NAME` in. Default: current directory. |
| `--profile` | `web-core` (default), `full-stack`, `native-ios`. See below. |
| `--set NAME=VALUE` | A web-layer option the profile declares. Repeatable. Booleans accept only `true`/`false` (`yes/no/on/off/1/0` are parsed by devkit; the template is the final judge). |
| `--template-ref vX.Y.Z` | A specific supported release instead of the newest. Outside the range → exit 2. |
| `--template PATH` | **Development:** render a local checkout *as it is on disk*. Records a home-relative path; not for sharing. |
| `--template URL` | Another origin with the same release rules. |
| `--native-template`, `--native-template-ref`, `--native-set` | The native layer's equivalents (`native-ios` profile only; refused for others). |
| `--dry-run` | Resolve and preview with Copier's `pretend`; write nothing. |

**Web options** (`--set`), with the first template release that has each:

| Option | Values | Default | Since | Requires | Sticky |
|---|---|---|---|---|---|
| `cache_components` | bool | `true` | 0.1.0 | – | no |
| `zod` | bool | `false` | 0.2.0 | – | no |
| `forms` | bool | `false` | 0.3.0 | `zod` | no |
| `rest_api` | bool | `false` | 0.4.0 | `zod` | no |
| `database` | `none` \| `postgres` \| `supabase` | `none` | 0.5.0 | `zod` | **yes** |
| `auth` | bool | `false` | 0.6.0 | `zod`, `rest_api`, a `database` | **yes** |
| `native_client` | bool | `false` | 0.7.0 | `auth` | **yes** |

`devkit` knows names, types, defaults, `since` and stickiness; the **requires** rules are enforced only by the template's `copier.yml` validators, and `devkit` reports their rejection as exit 2.

**Profiles.**

| Profile | Fixed options | You must set | Layers |
|---|---|---|---|
| `web-core` | none | nothing | web |
| `full-stack` | `zod`, `rest_api`, `auth` = true | `database=postgres\|supabase` | web |
| `native-ios` | the above + `native_client` = true | `database=postgres\|supabase` | web + native |

A fixed option may be repeated with the same value; a different value is refused.

**Order of checks** (cheap first, nothing touched on bad input): profile → name → option parsing → profile rules → native options → destination → release resolution (`git ls-remote --tags`) → `since` gate → native pair check → render → verify each requested option was recorded in the answers file.

**Examples.**

```bash
uv run devkit new my-app --output-dir ..
uv run devkit new my-app --set zod=true --set rest_api=true --output-dir ..
uv run devkit new shop --profile full-stack --set database=supabase --set forms=true --output-dir ..
uv run devkit new notes --profile native-ios --set database=postgres --native-set bundle_identifier=com.acme.notes --output-dir ..
uv run devkit new scratch --template ../web-core-template --output-dir /tmp   # template development
```

**Failure modes.**

| Message (abridged) | Exit | Meaning |
|---|---|---|
| `Destination already exists` | 1 | Pick another name or `--output-dir`. |
| `Destination is inside the developer-platform checkout` | 1 | Generate outside the checkouts. |
| `Template source is unavailable` | 1 | Network, URL, or private-repo credentials. |
| `No supported template release found` | 1 | The origin has no tag inside the range. |
| `.NAME.devkit-partial exists from an earlier failed run` | 1 | Inspect and remove it yourself ([recovery](../upgrade/recovery.md#a-failed-two-layer-generation-devkit-partial)). |
| `Unknown option 'x' for this profile` | 2 | Typo, or the option belongs to `--native-set`. |
| `Option 'native_client' needs template v0.7.0 or newer` | 2 | `--template-ref` too old for the option. |
| `Validation error for question 'forms': forms requires zod` | 2 | Template rule; add the prerequisite explicitly. |
| `Profile 'full-stack' needs an explicit choice for database` | 2 | Add `--set database=postgres` or `supabase`. |
| `native-ios-template v0.1.1 works with web-core-template >=0.7.0,<0.8.0` | 2 | Incompatible pair of releases. |

---

## devkit status

**Purpose.** Read-only: show each template layer of a project, its installed release and the newest supported release at its recorded origin.

```bash
uv run devkit status PROJECT
```

```text
web     v0.7.0    up to date
native  v0.1.1    up to date
```

**Failure modes.** Exit 1 if the project has no answers file, or if the two installed releases do not belong together (`warning: native v0.1.1 works with web >=0.7.0,<0.8.0 …`). It reads remote tags, so it needs template access; an unreachable origin is shown as a note rather than an error.

---

## devkit upgrade

**Purpose.** Move a project (one layer at a time) to a newer supported template release with Copier's three-way merge, keeping your answers and your edits.

```bash
uv run devkit upgrade PROJECT [--to vX.Y.Z] [--set NAME=VALUE ...] [--layer auto|web|native]
                              [--profile …] [--dry-run]
```

| Option | Meaning |
|---|---|
| `--dry-run` | Print the plan and run Copier's preview; change nothing. Always do this first. |
| `--to` | A specific supported release (newer than installed). Downgrades are refused. |
| `--set` | Change an option while upgrading (for example enable `forms`). Sticky options cannot change once set. With no newer release, `--set` re-renders the installed release. |
| `--layer` | `web` or `native`. **Required** when `.copier-answers.ios.yml` exists; `auto` means web in a one-layer project. |

**Guarantees and refusals:** project must be a Git root with nothing modified or untracked (exit 1); installed release must be a plain tag inside the range (exit 1 for commits after a tag, exit 2 for out-of-range); target must exist and be newer; a step that would break the web/native pair is refused (exit 2); after Copier runs, the recorded `_commit` must equal the target and every `--set` must be recorded; conflicts → exit 3 with the file list. It never commits.

```bash
uv run devkit upgrade ../my-app --dry-run
uv run devkit upgrade ../my-app
uv run devkit upgrade ../my-app --set forms=true
uv run devkit upgrade ../notes --layer web --dry-run
uv run devkit upgrade ../notes --layer native
```

After a successful upgrade it prints the next steps: `git diff`, `npm ci && npm run check` (web) or `sh ios/scripts/check-contract.sh && sh ios/scripts/test.sh` (native), then commit. If the other layer is behind, it says **NOT fully upgraded**. Full procedure: [Upgrading the web layer](../upgrade/web.md) and [Two-layer projects](../upgrade/layers.md).

---

## devkit native add

**Purpose.** Apply the native iOS layer to an existing full-stack project.

```bash
uv run devkit native add PROJECT [--native-template PATH_OR_URL] [--native-template-ref REF]
                                 [--native-set NAME=VALUE ...] [--dry-run]
```

Requires: a clean Git root; `.copier-answers.yml` with `zod`, `rest_api`, `auth` true and a database; **`native_client: true`** (otherwise it stops and tells you to run `devkit upgrade PROJECT --set native_client=true` first); no existing `ios/` or `.copier-answers.ios.yml`; a compatible release pair. It adds only `ios/` and `.copier-answers.ios.yml`.

**Failure modes.** Exit 2 for a missing prerequisite (listed by name) or `native_client` off; exit 1 for a dirty tree or an existing `ios/`. If Copier fails part-way, nothing of yours is removed (`cleanup_on_error=False`); inspect `git status`.
