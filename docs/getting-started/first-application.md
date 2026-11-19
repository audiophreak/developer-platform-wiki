# Create your first Web Core application

This walkthrough follows Developer Platform `v0.2.0` and Web Core Template `v0.1.0` source. It creates a new Web Core project from a sibling checkout layout; adjust `--output-dir` for your own folder structure.

## Before starting

- Read [the platform overview](platform-overview.md) and understand the released baseline.
- Check out both private repositories and have Git configured to authenticate non-interactively. The platform's publishing guide recommends `gh auth setup-git`.
- Install Python 3.12+, uv, Git 2.27+, and Node.js 26.x. `devkit doctor` checks required tools and reports optional tools.
- Decide on an application name, repository location, initial feature set, and whether you need optional capabilities.

## Provision, inspect, validate

1. In the `developer-platform` checkout, install project dependencies and run the read-only prerequisite check:

   ```bash
   uv sync
   uv run devkit doctor
   ```

2. Preview what will be generated. The example assumes `developer-platform` and `web-core-template` checkouts are sibling folders and creates the app beside them:

   ```bash
   uv run devkit new my-first-app --description "My first Web Core application" --output-dir .. --dry-run
   ```

3. Generate it by removing `--dry-run`:

   ```bash
   uv run devkit new my-first-app --description "My first Web Core application" --output-dir ..
   ```

4. The v0.1.0 template asks for `app_name`, `app_description`, and `cache_components` (default `true`). The CLI always supplies name and description; use `--set cache_components=false` to turn off Next.js Cache Components and Partial Prefetching.
5. Inspect `.copier-answers.yml`, `package.json`, `.nvmrc`, `AGENTS.md`, and the generated CI workflow. The answers record the template URL and rendered ref. The template uses no Copier tasks, migrations, or Jinja extensions, so generation itself executes no template hook code.
6. Enter the app directory and install exactly from the committed lockfile, then run the complete gate:

   ```bash
   cd ../my-first-app
   npm ci
   npm run check
   ```

   `npm run check` runs lint, typecheck, format check, Vitest, and a production build.
7. Connect the generated project to a private repository when ready. Do not publish it publicly by default; review credentials and repository visibility first.
8. Commit the baseline along with `.copier-answers.yml`, which Copier uses for a later three-way template update.

## What success looks like

The new project has a clean baseline check; generated configuration matches your answers; `.copier-answers.yml` records template provenance; and local validation agrees with the template CI workflow. Template changes do not flow into this generated application automatically; see [upgrade lifecycle](../architecture/upgrade-lifecycle.md).

## If it fails

Record the exact command, exit code, runtime versions, and relevant non-secret output. Compare the generated app's own README and lockfiles before changing dependencies. See [dependency troubleshooting](../operations/dependencies.md) and [build troubleshooting](../operations/build-errors.md).
