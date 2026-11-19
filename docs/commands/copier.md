# Copier

[Copier](https://copier.readthedocs.io/) 9.19.1 is the template engine. `devkit` calls it through its Python API (`copier.run_copy`, `copier.run_update`) with fixed, safe settings. You run the `copier` command directly only to develop a template or in exceptional recovery. Copier is installed in each repository's `.venv` by `uv sync`; use `uv run copier`.

## What devkit passes, and why

| Setting | Value in `devkit` | Why |
|---|---|---|
| `vcs_ref` | always explicit: a release tag (published) or `HEAD` (local) | Copier otherwise renders the newest tag and ignores uncommitted work |
| `settings` | `Settings()` (empty) | ignore any user-level Copier settings |
| `unsafe` | `False` | templates contain no `_tasks`, `_migrations` or Jinja extensions; nothing executes |
| `defaults` | `True` | non-interactive; answers come from `--set` or defaults |
| `overwrite` | `False` for copy, `True` for update | never overwrite on creation; update merges |
| `conflict` | `inline` (update) | markers in files, never `.rej` files |
| `skip_answered` | `True` (update) | keep recorded answers |
| `cleanup_on_error` | `True` for the first layer's copy; `False` for the native layer and for updates | never remove anything that existed before |
| `answers_file` | `.copier-answers.yml` or `.copier-answers.ios.yml` | each layer has its own record |

## copier copy

**Purpose.** Render a template into a directory.

```bash
# from a template checkout, rendering the working tree (template development)
uv run copier copy --vcs-ref HEAD --defaults --data app_name=scratch-app . ../scratch-app

# from the published origin at an explicit release
uv run copier copy --vcs-ref v0.7.0 --defaults \
  --data app_name=my-app --data zod=true \
  https://github.com/audiophreak/web-core-template.git ../my-app

# the native layer into an existing web project (from its root, clean tree)
uv run copier copy --vcs-ref v0.1.1 --data app_name=my-app \
  https://github.com/audiophreak/native-ios-template.git .
```

| Option | Meaning |
|---|---|
| `-r, --vcs-ref REF` | Git ref to render. **Always pass it.** |
| `-d, --data NAME=VALUE` | Answer a question. Booleans are strict in these templates. |
| `-l, --defaults` | Use defaults for unanswered questions; no prompts. |
| `-n, --pretend` | Preview; write nothing. |
| `--trust` | Allow unsafe features. **Never needed** for these templates; a test in each template fails if one would require it. |

**Failure modes.** `Validation error for question '…'` (an answer broke a `copier.yml` validator; nothing written). Git authentication errors for the private origin. Without `--vcs-ref`, a surprise: the newest tag, even one your `devkit` does not support.

## copier update

**Purpose.** Three-way merge a newer template release into an existing project: old release render ↔ new release render ↔ your files.

```bash
git status                                         # must be clean
uv run copier update --vcs-ref v0.7.0 --defaults --skip-answered
uv run copier update --vcs-ref v0.7.0 --defaults --skip-answered --data rest_api=true   # enable a feature
uv run copier update --answers-file .copier-answers.ios.yml --vcs-ref v0.1.1 --defaults --skip-answered  # native layer
```

| Option | Meaning |
|---|---|
| `-r, --vcs-ref` | The target release. Without it: the newest tag, possibly outside the supported range. |
| `-A, --skip-answered` | Do not re-ask recorded questions. |
| `-a, --answers-file` | Which layer. **Required for the native layer**: without it Copier reads the web answers. |
| `-o, --conflict inline\|rej` | Conflict style; `inline` keeps both sides in the file. |
| `-n, --pretend` | Preview. |

!!! danger "Raw `copier update` bypasses every platform protection"
    It does not enforce the supported range, does not keep an established database provider or `auth` (a Copier validator cannot see the previous answer), does not refuse a two-layer project without `--answers-file`, does not check the release pair, and **exits 0 even when it leaves conflict markers**. Use `devkit upgrade`; if you must use Copier, pin `--vcs-ref`, pass the right `--answers-file`, and search for `<<<<<<<` afterwards.

## The answers file

```yaml
_commit: v0.7.0                                              # the release rendered
_src_path: https://github.com/audiophreak/web-core-template.git  # where it came from
app_name: my-app
zod: true
...
```

Commit it; never edit it by hand. Computed values (`has_database`, `has_server`, `lock_key`) are `when: false` questions and are never recorded. If the template repository moves, `_src_path` is the one field you may change deliberately.
