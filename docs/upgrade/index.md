# Upgrade and Recovery

## Philosophy

1. **Git is the rollback.** Every upgrade starts from a clean, committed tree, so your work is always recoverable and never mixed with template changes. `devkit` never commits, so you review before anything is recorded.
2. **Never discard, never delete.** Upgrades merge; conflicts are left inline with both sides kept; `cleanup_on_error` is off for updates; a failed two-layer generation leaves its partial result for you to inspect.
3. **Never guess.** No architecture is chosen for you, no prerequisite is switched on, no layer is picked in a two-layer project, no unsupported release is used.
4. **One step, one review, one commit.** One target release per upgrade; one layer per upgrade; each committed on its own.
5. **Fix forward.** Published tags never move. A bad release is followed by a patch release, not a re-tag.

## The layered upgrade workflow

```mermaid
flowchart TD
  s([Project with two layers]) --> st[devkit status PROJECT]
  st --> clean{git status clean?<br/>no modified, no untracked}
  clean -- no --> fix["commit or git stash -u<br/>ignore build artifacts"] --> clean
  clean -- yes --> br[git switch -c chore/template-upgrade]
  br --> which{Which layer is behind?}
  which -- web --> wdry["devkit upgrade P --layer web --dry-run"]
  wdry --> pair{Target web release still<br/>in NATIVE_REQUIRES_WEB<br/>for the installed native?}
  pair -- no --> stop[exit 2: upgrade the native layer first<br/>once a release for the new contract exists]
  pair -- yes --> wrun["devkit upgrade P --layer web"]
  which -- native --> ndry["devkit upgrade P --layer native --dry-run"]
  ndry --> npair{Target native needs a web<br/>release the project has?}
  npair -- no --> stop2[exit 2: upgrade the web layer first]
  npair -- yes --> nrun["devkit upgrade P --layer native"]
  wrun --> conf{exit 3?}
  nrun --> conf
  conf -- yes --> resolve["resolve conflict markers<br/>git add"] --> verify
  conf -- no --> verify[review git diff<br/>web: npm ci + npm run check<br/>native: check-contract.sh + test.sh]
  verify --> commit["git commit -m 'chore: update LAYER template'"]
  commit --> more{devkit status:<br/>NOT fully upgraded?}
  more -- yes --> which
  more -- no --> done([Merge the branch])
```

## Pages

| Page | Covers |
|---|---|
| [Upgrading the web layer](web.md) | `devkit upgrade`, enabling features, sticky options, Copier merges, preserving edits |
| [Two-layer projects](layers.md) | `--layer`, `devkit status`, `native add`, pair compatibility, raw Copier hazards |
| [Recovery procedures](recovery.md) | clean-tree requirements, `.devkit-partial`, interrupted operations, conflicts, rollback |
