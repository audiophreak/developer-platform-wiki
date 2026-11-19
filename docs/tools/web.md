# Web application toolchain

All versions are exact pins in `web-core-template/template/package.json.jinja` at `v0.7.0`, unchanged in `v0.7.1`, each at least two weeks old when chosen.

## Node.js, fnm and npm

| | |
|---|---|
| **Problem** | Running the web toolchain and server with a known runtime and a reproducible dependency tree. |
| **Why selected** | Next.js's runtime; `.nvmrc` + `engines` is read by fnm, nvm, mise and `actions/setup-node`, so no extra tool is needed. fnm is in the Brewfile; mise was evaluated and not adopted (a second source of truth and a shell hook for no gain). |
| **Invoked by** | You, `npm` scripts, CI (`setup-node` with `node-version-file: .nvmrc`), `e2e.mjs`. |
| **Consumes / produces** | `package.json`, `package-lock.json`, `.npmrc` → `node_modules/`. |
| **Phase** | Development, runtime, CI. |
| **Caveats** | Node **26** only (`>=26 <27`); use `npm ci`, not `npm install`; `devkit doctor` fails on another major. |

## Next.js 16.4.5 and React 19.3.0

| | |
|---|---|
| **Problem** | One framework for server-rendered UI, route handlers (the REST API) and the auth handler. |
| **Why selected** | The reference Web Core application was a `create-next-app` scaffold; the template was derived from it and keeps its App Router layout. |
| **Invoked by** | `npm run dev/build/start/typecheck`; `e2e.mjs` runs `next start`. |
| **Produces** | `.next/` build output, route types. |
| **Caveats** | `cache_components=true` (default) enables `cacheComponents` and `partialPrefetching` together (Next.js requires the first for the second): dynamic by default, opt-in `use cache`, Node.js runtime only. `next/font/google` needs network at build. Read `node_modules/next/dist/docs/` before writing code (the generated `AGENTS.md` says so). |

## TypeScript 5.9.3

Strict mode (`tsconfig.json`); `next typegen` generates route types before `tsc --noEmit`. **Phase:** development, CI. `allowJs: true` is the scaffold default and kept.

## Tailwind CSS 4.3.5 and shadcn/ui

| | |
|---|---|
| **Problem** | Styling and accessible primitives without a design system to maintain. |
| **Why selected** | Tailwind v4 with Turbopack (`@tailwindcss/turbopack` wired in `next.config.ts`, no PostCSS config); shadcn/ui copies components into the project (`src/components/ui`), built on Radix (`radix-ui` 1.8.1) and Lucide icons, with `class-variance-authority`, `tw-animate-css`. |
| **Invoked by** | The build; `npx shadcn add …` (dev dependency 4.23.0). |
| **Caveats** | `Button` is the only shipped component (the reference). Adding components is a dependency decision. |

## ESLint 9.39.5 and Prettier 3.9.10

Lint (flat config with `eslint-config-next` and `eslint-config-prettier`) and formatting, both part of `npm run check`. In native projects both ignore `ios/` and `.copier-answers.ios.yml`. **Phase:** development, CI.

## Vitest 5.0.5

| | |
|---|---|
| **Problem** | Fast unit, component, handler and real-database tests in one runner. |
| **Why selected** | Native ESM/TypeScript; resolves the `@/*` alias from `tsconfig.json`. |
| **Invoked by** | `npm run test` (`vitest.config.mts`, excludes `*.db.test.ts`), `npm run test:db` (`vitest.db.config.mts`), `openapi:generate` (runs the contract test with writing on). |
| **Caveats** | `server-only` is aliased to a stub in tests. DOM tests opt in with `// @vitest-environment jsdom` (Forms: `jsdom` 30.1.3, Testing Library). |

## Zod 4.6.7

| | |
|---|---|
| **Problem** | One definition of every input and output shape, usable on client and server, and convertible to JSON Schema. |
| **Why selected** | `safeParse` at trust boundaries; `z.toJSONSchema` feeds the OpenAPI generator. It was the first feature because everything after it depends on it. |
| **Used by** | Forms (client), route handlers (server), repositories (DB input/output), configuration loaders, the OpenAPI document. |
| **Phase** | Runtime, development (contract generation). |
| **Caveats** | Schemas in `src/lib/schemas/` must stay free of framework, environment and database imports (a test enforces it). |

## React Hook Form 7.91.0 (+ `@hookform/resolvers` 5.9.2)

Optional `forms` feature: an accessible example form at `/forms-example` validated by the shared Zod schema through `zodResolver`; saves and sends nothing. **Phase:** runtime.

## pg 8.23.1 and server-only 0.0.1

`pg` is the PostgreSQL client used by both the repository layer and Better Auth (one pool per server process). `server-only` makes the build fail if a client component imports a server module. **Phase:** runtime.
