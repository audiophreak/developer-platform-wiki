# Command reference

## Developer Platform v0.2.0

Run from the `developer-platform` checkout:

```bash
uv sync
uv run devkit doctor
uv run devkit new my-app --description "What it does" --output-dir .. --dry-run
uv run devkit new my-app --description "What it does" --output-dir ..
uv run devkit new my-app --set cache_components=false --output-dir ..
```

`--dry-run` writes nothing. `--template PATH` is for local template development; `--template-ref` selects an exact tag/ref. `--profile full-stack` and `native-ios` are reserved and rejected in v0.2.0.

## Generated Web Core app v0.1.0

```bash
npm ci
npm run dev
npm run lint
npm run typecheck
npm run test
npm run format:check
npm run build
npm run check
```

`npm run check` runs lint, typecheck, formatting, tests, and production build. See the [first-app tutorial](../getting-started/first-application.md) and [release reference](releases.md).
