# Next.js, TypeScript, ESLint, Prettier, Vitest

You normally reach these through `npm run …` ([npm](npm.md)). Direct invocations below are for diagnosis. Run them with `npx` from the project root so the pinned versions are used.

| Tool | Version | Config file |
|---|---|---|
| Next.js | 16.4.5 | `next.config.ts` |
| React / React DOM | 19.3.0 | – |
| TypeScript | 5.9.3 | `tsconfig.json` (strict) |
| ESLint | 9.39.5 (+ `eslint-config-next` 16.4.5, `eslint-config-prettier` 10.1.8) | `eslint.config.mjs` |
| Prettier | 3.9.10 | `.prettierrc.json`, `.prettierignore` |
| Vitest | 5.0.5 (Vite 8.3.5) | `vitest.config.mts`, `vitest.db.config.mts` |
| Tailwind CSS | 4.3.5 (`@tailwindcss/turbopack`) | wired in `next.config.ts` `turbopack.rules` |
| shadcn CLI | 4.23.0 (dev) | `components.json` |

## Next.js

```bash
npx next dev                 # = npm run dev
npx next build               # = npm run build
npx next start -p 3000       # serve the build (the e2e script runs next start on a free port)
npx next typegen             # generate route types (part of npm run typecheck)
```

!!! warning "This is not the Next.js in most training data"
    The generated `AGENTS.md` begins with a block (written by `next dev` itself) telling agents to read the docs bundled in `node_modules/next/dist/docs/` before writing code: Next.js 16 changed APIs and conventions. With `cache_components=true` (the default), data fetching is dynamic by default and caching is opt-in with `use cache`; database reads go inside a `Suspense` boundary after `await connection()`.

**Failure modes.** `next build` fetches Google Fonts (Geist via `next/font/google`), so it needs network. A server-only module imported from a client component fails the build (`server-only`).

## TypeScript

```bash
npx tsc --noEmit             # after `npx next typegen`
```

## ESLint and Prettier

```bash
npx eslint .                 # or a path
npx eslint . --fix
npx prettier --check .
npx prettier --write src/app/page.tsx
```

In a native project, `eslint.config.mjs` and `.prettierignore` exclude `ios/` and `.copier-answers.ios.yml`: the web tooling must not format another template's files. `.prettierignore` also excludes the root `.copier-answers.yml` (Prettier rejected Copier's quoting of an all-digit `_commit`).

## Vitest

```bash
npx vitest run                               # = npm run test
npx vitest run src/server/auth/guard.test.ts # one file
npx vitest                                   # watch mode
npx vitest run --config vitest.db.config.mts # = npm run test:db
```

Conventions in generated projects: `*.test.ts(x)` beside the code; `*.db.test.ts` for tests that need PostgreSQL (excluded from `npm run test`); DOM tests declare `// @vitest-environment jsdom` (Forms feature). Tests alias `server-only` to a stub because it throws outside the Next.js server bundle.

## shadcn/ui

```bash
npx shadcn add card          # adds a component to src/components/ui (a dependency change: needs approval)
```
