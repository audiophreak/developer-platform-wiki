# Two-layer projects

A `native-ios` project has two Copier templates applied to one directory, each with its own answers file and releases. They are upgraded **one at a time**, each from a clean tree, each reviewed and committed on its own, so one layer's changes can never hide inside the other's and a failure in one never leaves the project looking fully upgraded.

## `devkit status`

```bash
uv run devkit status PROJECT
```

```text
web     v0.7.0    up to date
native  v0.1.1    up to date
```

When something is newer:

```text
web     v0.7.0    newer available: v0.7.1
native  v0.1.1    up to date

The project is NOT fully upgraded. Upgrade one layer at a time: devkit upgrade PROJECT --layer web|native
```

If the installed pair does not belong together, `status` prints `warning: native v0.1.1 works with web >=0.7.0,<0.8.0, but the web layer is at …` and exits 1.

## `--layer`

```bash
devkit upgrade PROJECT --layer web    [--to vX.Y.Z] [--set …] [--dry-run]
devkit upgrade PROJECT --layer native [--to vX.Y.Z] [--set …] [--dry-run]
```

- Without `--layer` (or with `--layer auto`) in a two-layer project: **refused** (exit 2): `… has a web layer and a native iOS layer, each with its own releases. Choose one: --layer web or --layer native`.
- `--layer native` in a project without `.copier-answers.ios.yml`: refused.
- `--set` with `--layer native` sets native answers (`app_display_name`, `bundle_identifier`, `debug_api_port`, `release_api_host`).
- After one layer, if the other has a newer release, the command prints **`NOT fully upgraded: <layer> layer: vA -> vB available. Commit this first, then devkit upgrade PROJECT --layer <other>.`**
- A merge conflict in one layer exits 3; the other layer is untouched.

## Version-pair compatibility

`NATIVE_REQUIRES_WEB` in `profiles.py` is the source of truth: native `0.1.x` ↔ web `>=0.7.0,<0.8.0`.

| Situation | `devkit` |
|---|---|
| upgrade web to a release outside the installed native's range | refused: *upgrade the native layer first (once a release for the new web contract exists), or stay on a web release in that range* |
| upgrade native to a release that needs a newer web | refused: *upgrade the web layer first* |
| a native release this devkit does not know | refused at `new`; reported by `status` |
| both within range | allowed |

Why: the native app's Swift client is generated from one web release's OpenAPI contract. A web release with a different contract would leave the client out of step with the server. Web patch releases within 0.7.x keep the pair valid.

After **any** web-layer upgrade in a native project, verify the contract is still shared:

```bash
npm run openapi:generate && git diff --exit-code openapi/
sh ios/scripts/check-contract.sh
```

If the contract changed, `sh ios/scripts/sync-contract.sh`, fix and test the app, and commit with the web upgrade.

## Safe native additions

`devkit native add PROJECT` is the only supported way to add the native layer later, and it is purely additive:

- requires a clean, committed Git root;
- requires `zod`, `rest_api`, `auth` true and a database (lists what is missing);
- requires **`native_client: true`**; if off, it stops and tells you to run `devkit upgrade PROJECT --set native_client=true`, review and commit, then retry (it does not switch it on for you);
- refuses if `ios/` or `.copier-answers.ios.yml` already exists;
- checks the release pair;
- writes only `ios/` and `.copier-answers.ios.yml`; `git status` afterwards shows exactly those two as new.

## Raw Copier on a two-layer project

!!! danger "Pass the answers file, or Copier updates the wrong layer"
    `copier update` without `--answers-file .copier-answers.ios.yml` reads the **web** layer's answers. For the native layer:

    ```bash
    copier update --answers-file .copier-answers.ios.yml --vcs-ref v0.1.x --defaults --skip-answered
    ```

    Raw Copier also does not check the release pair. Prefer `devkit upgrade PROJECT --layer native`.

!!! note "Fixed in native v0.1.1"
    The generated `ios/README.md` of native **v0.1.0** named a devkit subcommand that does not exist. From **v0.1.1** it documents exactly this workflow: `devkit status PROJECT`, `devkit upgrade PROJECT --layer native` and `--layer web` (with `--dry-run`), one layer at a time from a clean tree, and the raw Copier command with its required `--answers-file`. A regression test in the template checks every documented devkit command against devkit 0.8.0's command line.

## Upgrading a v0.1.0 native layer to v0.1.1

Verified in the published acceptance (devkit v0.8.0 unchanged):

```bash
devkit status PROJECT                          # native  v0.1.0    newer available: v0.1.1
git -C PROJECT status --porcelain              # must be empty; if it lists ?? ios/.derived-data-release.log
                                               # (left by the v0.1.0 Release check), move that file out of the project
devkit upgrade PROJECT --layer native --dry-run    # Upgrading v0.1.0 -> v0.1.1
devkit upgrade PROJECT --layer native
git -C PROJECT status --short                  # exactly: .copier-answers.ios.yml, ios/README.md, ios/scripts/check-release-config.sh
git -C PROJECT add -A && git -C PROJECT commit -m "chore: update native template to v0.1.1"
```

No web-layer change is involved: native 0.1.x pairs with web `>=0.7.0,<0.8.0`, so the pair rule is satisfied before and after.
