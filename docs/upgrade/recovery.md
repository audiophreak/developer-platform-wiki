# Recovery procedures

Every procedure here uses Git's non-destructive commands and the platform's validated helper. **Never** use `git reset --hard`, `git clean`, `rm -rf` or forced pushes: the platform's rules forbid them, and none is needed.

## The clean-tree requirement

`devkit upgrade` and `devkit native add` require `git status --porcelain -uall` to be empty: nothing modified, nothing staged, **nothing untracked**.

```bash
git status --short
```

| You see | Do |
|---|---|
| your own work in progress | `git add -A && git commit -m "wip: …"` on a branch, or `git stash -u` |
| `?? supabase/.temp/`, `?? supabase/.branches/` (pre-0.6.0 Supabase project) | add both to `.gitignore`, commit |
| `?? ios/.derived-data-release.log` (after `check-release-config.sh`) | add `ios/.derived-data-release.log` to `.gitignore` and commit, or move the file out of the project |
| `?? .env.local` | should be ignored (`.env*`); if not, your `.gitignore` was edited: restore the template's line |
| `M AGENTS.md` (the Next.js agent block re-added) | `next dev` writes that block; commit it (the generated `AGENTS.md` says removing it only re-creates the change) |

## An interrupted or failed upgrade

The upgrade started from a commit, so that commit is the rollback.

```bash
git status                       # what changed
git diff                         # inspect
git stash -u                     # set the whole attempt aside (keeps it, recoverable with git stash pop)
# or, file by file:
git restore --source=HEAD --staged --worktree -- path/to/file
```

If you upgraded on a branch, `git switch main` leaves the attempt on the branch. Re-run `devkit upgrade --dry-run` once the cause is fixed.

`devkit` reports `Copier finished but the recorded version is …, not vX.Y.Z` if the answers file did not end at the target: inspect with `git status`/`git diff`, stash, and retry.

## Merge conflicts (exit 3)

```text
error: Upgraded to v0.7.0 with merge conflicts in: package.json, src/app/globals.css. Nothing was discarded:
both sides are kept between <<<<<<< and >>>>>>> markers. Edit those files, then `git add` and commit; `git diff`
shows everything that changed.
```

```bash
grep -rn '^<<<<<<< ' --exclude-dir=node_modules --exclude-dir=.next .
$EDITOR package.json src/app/globals.css
npm install          # only if package.json changed: repairs package-lock.json
npm run check
git add -A && git commit -m "chore: update web template to v0.7.0"
```

## A failed two-layer generation (.devkit-partial)

Symptom: `devkit new … --profile native-ios` failed; nothing exists at `NAME`; a hidden `OUTPUT_DIR/.NAME.devkit-partial` exists. A retry fails with `… exists from an earlier failed run. Inspect it, remove it yourself, and retry.`

1. Read the original error. `The web layer was generated but the project is incomplete and was NOT moved into place; inspect …` means the native layer failed.
2. Inspect the staging directory: `ls -la OUTPUT_DIR/.NAME.devkit-partial` (web files present? `ios/` partial?).
3. Fix the cause (network or credentials for the native template, an invalid `--native-set` value, an incompatible `--native-template-ref`).
4. Remove the staging directory **with the validated helper**, or move it aside:

    ```bash
    # move it out of the way (always safe)
    mv OUTPUT_DIR/.NAME.devkit-partial "$(mktemp -d)/"
    ```

    If you generated into a `tools/scratch.py` workspace, `uv run python tools/scratch.py clean WORKSPACE .NAME.devkit-partial` removes it after validating it is inside that workspace.

5. Retry `devkit new`.

`devkit` never deletes the staging directory itself, by design.

## A failed single-layer generation

Copier removes the directory it created (`cleanup_on_error=True`). If the message says `Partial output may remain at …`, inspect it before deciding; it never contains anything of yours because the destination was required not to exist.

## A failed `devkit native add`

Nothing of yours is removed (`cleanup_on_error=False`). `git status` shows what was added; `git stash -u` sets it aside; fix the cause and retry.

## Database state

| Situation | Recovery |
|---|---|
| migration failed | it was rolled back and not recorded; fix in a **new** migration if the file was committed, else edit, `db:lock`, `db:migrate` |
| "was modified after it was locked/applied" | `git restore --source=HEAD -- supabase/migrations/<file>`; put the change in a new migration |
| local data must go (postgres) | `docker compose --env-file .env.local down --volumes` (deletes the volume), then `db:init` only if `.env.local` is gone, `db:up`, `db:migrate` |
| local data must go (supabase) | `npx --no-install supabase db reset` (local only), then `npm run db:roles` |
| backup first | `docker compose --env-file .env.local exec db pg_dump -U app app > backup.sql` (keep it out of Git) |

## Version-pair recovery

If `devkit status` reports the two layers do not belong together (for example after a raw `copier update`), return the offending layer to its last committed state (`git restore --source=HEAD~1 -- <that layer's files and answers file>` on a branch, or revert the commit with `git revert <sha>`), then upgrade in the supported order.

## Rollback of a published release

Not possible by design: tags are immutable. Release a patch that reverts the change (`git revert` on a branch, PR, CI, new tag), then widen or keep the platform range as appropriate.
