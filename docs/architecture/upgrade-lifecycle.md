# Application upgrade lifecycle

**Released behavior and draft behavior are separated here.** Web Core template v0.1.0 documents `copier update`; it requires a clean Git tree and explicit target release tag, then performs a three-way merge. `devkit upgrade` is in an open draft platform PR proposing v0.3.0 and is not released.

For v0.1.0-generated applications, commit `.copier-answers.yml` and do not edit it by hand. With a clean tree and private-template Git access, choose an explicit compatible release and run `copier update --vcs-ref <tag> --defaults --skip-answered`. Review inline conflict markers; resolve `package.json` then regenerate `package-lock.json` with `npm install`; run `npm run check`. The template guide says new questions take defaults unless overridden with `--data`. Never omit `--vcs-ref`, since Copier otherwise selects the newest tag.

Draft platform PR #1 proposes `devkit upgrade` with `--dry-run`, `--to`, and `--set`, clean-tree enforcement, supported-range validation, preserved selections, and no auto-commit/delete behavior. Template PR #1 proposes optional features and backward compatibility. These remain proposed until merged and tagged. Follow [template upgrade workflow](../workflows/upgrades.md) for the released path.
