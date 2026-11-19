# Generated application structure

**Verified from the Web Core v0.1.0 tree.** The generated project is a conventional npm application with `package.json`, `package-lock.json`, `.nvmrc`, TypeScript and Next.js configuration, `src/app/`, `src/components/ui/`, and `src/lib/`. It includes `AGENTS.md` and `CLAUDE.md`, a Vitest configuration and component/page tests, formatting/lint configs, and `.github/workflows/ci.yml`.

The template renders a name/description-aware README, `package.json`, Next.js config, app-info JSON, and `.copier-answers.yml`. The main page and metadata read the generated description and name from `src/lib/app-info.json`. It starts with a small application shell rather than an imposed database/auth/API architecture; those decisions remain for the app owner.

The generated app has its own project lifecycle. `npm ci` consumes its lockfile; `npm run check` is its validation gate. Template source is not automatically synchronized into this repository. See [template provenance](template-versioning.md) and [first app tutorial](../getting-started/first-application.md).

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
