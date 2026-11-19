# Your first web project

The `web-core` profile (the default) generates a Next.js application with no optional features: strict TypeScript, Tailwind CSS v4, shadcn/ui, ESLint, Prettier, Vitest, a GitHub Actions workflow and AI instructions.

## 1. Preview

From the `developer-platform` checkout:

```bash
uv run devkit new my-app --description "What it does" --output-dir .. --dry-run
```

```text
[dry run] Profile 'web-core', published template https://github.com/audiophreak/web-core-template.git @ v0.7.0
...
Dry run complete. Nothing was written. Would create: <your home>/Developer/my-app
```

`devkit` resolved the **newest release tag this devkit supports** (`>=0.1.0,<0.8.0`, so `v0.7.0`) and Copier listed every file it would create. Nothing was written.

## 2. Generate

```bash
uv run devkit new my-app --description "What it does" --output-dir ..
```

Rules worth knowing now:

- `NAME` becomes the directory and the npm package name. The **template** validates it: lowercase letters, digits and single hyphens, 1–64 characters, starting with a letter. `devkit` itself only requires a safe single path segment.
- The description is optional (default `A Next.js application`) and restricted to a safe ASCII set.
- `devkit new` refuses any existing path at the destination (directory, empty directory, file or symlink) with exit 1, and never deletes anything.
- It does not run `git`, `npm` or `gh`, and creates no GitHub repository.

## 3. Commit the baseline

```bash
cd ../my-app
git init -b main && git add -A && git commit -m "chore: initial commit"
```

This is not ceremony. Upgrades need the project to be a Git repository root with a clean tree, so the first commit is your rollback point.

## 4. Install and validate

```bash
npm ci            # exact install from the committed package-lock.json
npm run check     # lint + typecheck + format:check + test + build
```

`npm run check` is the gate for every change in a generated project. It runs, in order: `eslint`, `next typegen && tsc --noEmit`, `prettier --check .`, `vitest run`, `next build`. On a basic project the acceptance run recorded **3 tests passed** and `npm audit --omit=dev` reported **0 vulnerabilities**.

## 5. Run it

```bash
npm run dev       # http://localhost:3000
```

## What you got

```text
my-app/
├── .copier-answers.yml        # template origin + release + your answers: commit it, never edit it
├── .github/workflows/ci.yml   # npm ci + npm run check, pinned actions, read-only permissions
├── .nvmrc                     # 26
├── AGENTS.md  CLAUDE.md       # rules for AI agents (CLAUDE.md imports AGENTS.md)
├── components.json            # shadcn/ui configuration
├── eslint.config.mjs  .prettierrc.json  .prettierignore
├── next.config.ts             # cacheComponents + partialPrefetching (cache_components=true)
├── package.json  package-lock.json
├── tsconfig.json  vitest.config.mts
└── src/
    ├── app/                   # layout.tsx, page.tsx, page.test.tsx, globals.css
    ├── components/ui/         # button.tsx (+ test): the reference shadcn component
    └── lib/                   # app-info.json (name, description), utils.ts
```

Look at the answers file:

```yaml title=".copier-answers.yml"
# Changes here will be overwritten by Copier; NEVER EDIT MANUALLY
_commit: v0.7.0
_src_path: https://github.com/audiophreak/web-core-template.git
app_description: What it does
app_name: my-app
auth: false
cache_components: true
database: none
forms: false
native_client: false
rest_api: false
zod: false
```

`_src_path` and `_commit` are the project's **provenance**: they are how `devkit upgrade` and `copier update` know where the project came from.

## Adding optional features at generation

Features are strict booleans (or, for `database`, a choice) set with `--set`. Prerequisites are enforced by the template and never switched on for you:

```bash
uv run devkit new my-app --set zod=true --set forms=true --output-dir ..
```

```text
error: Validation error for question 'forms': forms requires zod: answer zod=true as well (forms is never enabled for you).
```

That rejection (exit 2, nothing written) is what you get with `--set forms=true` alone. The full list is in [Feature composition](../architecture/feature-composition.md); the next page uses the `full-stack` profile, which fixes the common set for you.

## Push to GitHub (optional)

```bash
gh repo create my-app --private --source . --remote origin --push
```

The generated workflow then runs `npm ci` and `npm run check` on every push to `main` and every pull request.
