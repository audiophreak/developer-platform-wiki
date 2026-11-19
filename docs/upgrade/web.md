# Upgrading the web layer

## The procedure

```bash
cd PROJECT
git status                                     # must print nothing to commit, no untracked files
git switch -c chore/template-0.7.0             # optional, but makes the way back one command
uv run --project ~/Developer/developer-platform devkit upgrade . --dry-run
uv run --project ~/Developer/developer-platform devkit upgrade .
git diff                                       # review everything the template changed
npm ci                                         # the template ships the lock for your selection
npm run check
npm run test:db                                # if the project has a database
git add -A && git commit -m "chore: update web template to v0.7.0"
```

A real dry run (a `v0.6.1` web-core project with a local edit):

```text
[dry run] Project: .
[dry run] Template: https://github.com/audiophreak/web-core-template.git
[dry run] Upgrading v0.6.1 -> v0.7.0
[dry run] Keeping your answers: app_description=A Next.js application app_name=old-app auth=false cache_components=true database=none forms=false rest_api=false zod=false
[dry run] Note: this crosses a minor version, which may contain breaking changes; read the template CHANGELOG.
Dry run complete. Nothing was changed.
```

After the real run, the only change was `.copier-answers.yml` (`_commit: v0.7.0`, `native_client: false`), and the local edit to `src/app/page.tsx` was untouched, exactly as v0.7.0's byte-identity rule promises for a project with the new feature off.

## What `devkit upgrade` checks, in order

1. Arguments (`--to` is a release tag inside the range) before looking at the project.
2. The project has the answers file with `_src_path` and `_commit`.
3. **Clean Git root**: `git rev-parse --show-toplevel` equals the project; `git status --porcelain -uall` is empty.
4. The installed `_commit` is a plain release tag inside the supported range (`v0.6.1-3-gabc…` is refused: generated from unreleased commits).
5. Sticky options are not being changed.
6. The target exists at the recorded origin, is newer (no downgrades), and is inside the range.
7. The release pair still holds (two-layer projects).
8. Every `--set` option exists in the target release.
9. Copier `run_update` with `skip_answered`, `conflict="inline"`, `cleanup_on_error=False`, hermetic settings.
10. The recorded `_commit` equals the target; every `--set` is recorded; files with conflict markers are listed (exit 3).

## Preserving your modifications

Copier computes the diff between **the old release rendered with your answers** and **the new release rendered with your answers**, and applies it to **your current files**:

- a file you never touched gets the template's change;
- a file you changed in other places gets both changes;
- a file you added is never touched;
- a line both you and the template changed becomes an inline conflict, both sides kept.

`package.json`, `package-lock.json` and `globals.css` conflict most. For dependency conflicts: resolve `package.json` first, then run `npm install` to repair the lock (instead of hand-merging the lock), then `npm run check`.

## Enabling a feature on an existing project

```bash
devkit upgrade . --set zod=true                     # alone (re-renders the installed release) or with a newer release
devkit upgrade . --set forms=true                   # needs zod already
devkit upgrade . --set database=postgres            # needs zod; then: npm ci && npm run db:init && npm run db:up && npm run db:migrate
devkit upgrade . --set auth=true                    # needs zod, rest_api, a database; then: npm ci && npm run db:init && npm run db:migrate
devkit upgrade . --set native_client=true           # needs auth; then: npm run check (contract), commit, optionally devkit native add .
```

Prerequisites are never switched on for you; a missing one is exit 2 and nothing changes. After enabling `auth`, rows created earlier in `app.items` have no owner and are invisible to the application until you assign them (`update app.items set owner_id = '<user id>' where owner_id is null;`).

## What cannot be changed by an upgrade

| Change | Result | What to do instead |
|---|---|---|
| `database` postgres ↔ supabase, or to `none` | exit 2 | new project with the other provider; move data with `pg_dump`/`psql` |
| `auth=false` once true | exit 2 | manual removal ([Authentication](../web/authentication.md#removing-authentication)) |
| `native_client=false` once true | exit 2 | remove the bearer plugin and contract by hand |
| any feature off | not automated | delete its files and dependency by hand, or regenerate |
| several releases in one step | one target per run | upgrade, commit, upgrade again |

## Pre-0.6.0 Supabase projects

The Supabase CLI creates `supabase/.temp` and `supabase/.branches` on first start; templates before 0.6.0 did not ignore them, so the tree is "dirty" and the upgrade is refused. Add both paths to `.gitignore` and commit, then upgrade (the update itself brings the lines in).

## Raw `copier update`

Possible, but outside every guarantee: always pin `--vcs-ref` from the range your devkit supports, pass `--defaults --skip-answered`, search for `<<<<<<<` afterwards (it exits 0 with conflicts), and never use `--data` to change a sticky option.
