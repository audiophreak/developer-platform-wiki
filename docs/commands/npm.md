# npm and project scripts

npm 11 on Node 26 runs every generated web project. All dependencies are **exact-pinned** and the template ships a complete `package-lock.json` matching your feature selection, so no resolution happens on your machine.

## Installing

| Command | When | Notes |
|---|---|---|
| `npm ci` | After generation, after pulling, after an upgrade | Installs exactly the lockfile; fails if `package.json` and the lock disagree. **The normal command.** |
| `npm install` | Only to repair a lock after resolving a `package.json` merge conflict | Re-resolves; review the lock diff. |
| `npm install --save-exact pkg@x.y.z` | Adding or changing a dependency, **with approval** | Pick a release at least two weeks old; no install scripts. |
| `npm audit --omit=dev` | Production advisory check | 0 vulnerabilities in every acceptance project. |

Projects with `auth` carry `.npmrc` with `legacy-peer-deps=true`. Better Auth declares optional peers on frameworks and test runners; without the setting npm links the project's dev tools to them and reports their advisories in production audits. The lockfiles were produced under the same setting, so `npm ci` fails if it is removed.

## Scripts in every project

| Script | Runs | Purpose |
|---|---|---|
| `npm run dev` | `next dev` | Local development server (port 3000) |
| `npm run build` | `next build` | Production build |
| `npm run start` | `next start` | Serve the production build |
| `npm run lint` | `eslint` | Lint (flat config, `eslint-config-next` + Prettier compatibility) |
| `npm run typecheck` | `next typegen && tsc --noEmit` | Generate route types, then type-check |
| `npm run test` | `vitest run` | Unit and component tests (excludes `*.db.test.ts`) |
| `npm run format` | `prettier --write .` | Apply formatting |
| `npm run format:check` | `prettier --check .` | Verify formatting |
| `npm run check` | lint → typecheck → format:check → test → build | **The gate.** CI runs exactly this. |

### npm run check

The single gate for every web change, for people, agents and CI. It stops at the first failing step. Typical failures:

| Step fails | Usual cause | Fix |
|---|---|---|
| `lint` | a rule violation | fix the code; never disable the rule to pass |
| `typecheck` | type error, or stale route types | fix; `next typegen` runs first automatically |
| `format:check` | unformatted file | `npm run format` |
| `test` | a behaviour change without a test change, or a broken contract test | fix code or update the test deliberately |
| `test` (OpenAPI) | `openapi/openapi.json` stale | `npm run openapi:generate` and commit |
| `test` (migrations) | a committed migration edited, or a new one not locked | restore it, or `npm run db:lock` |
| `build` | server-only module imported by a client component; build-time network for fonts | fix the import boundary; ensure network |

## Scripts added by features

| Script | Feature | Purpose |
|---|---|---|
| `npm run db:init` | database | create `.env.local` (0600) with generated secrets; append only missing lines on an existing file |
| `npm run db:up` | database | start PostgreSQL (Compose) or the Supabase stack; wait for health; Supabase LAN-exposure check |
| `npm run db:down` | database | stop containers; **keep data** |
| `npm run db:status` | database | containers, migration state, runtime role attributes |
| `npm run db:logs` | database (postgres) | last database log lines |
| `npm run db:migrate` | database | apply pending migrations (local DB only), then provision `app_runtime`'s password |
| `npm run db:verify` | database | offline: migration files match `supabase/migrations.lock/` |
| `npm run db:lock` | database | record new migrations in the lock |
| `npm run db:roles` | auth | give `app_runtime` the password from `DATABASE_RUNTIME_URL` |
| `npm run test:db` | database | real-database tests (`vitest.db.config.mts`), each file in its own throwaway database |
| `npm run openapi:generate` | native_client | rewrite `openapi/openapi.json` from the Zod schemas, then verify it |

Details: [Database commands](database.md), [Better Auth operations](auth.md), [OpenAPI and Swift](openapi-swift.md).
