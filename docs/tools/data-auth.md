# Data and authentication

## Docker and Docker Compose

| | |
|---|---|
| **Problem** | Running PostgreSQL (or the Supabase stack) locally and in tests without installing a database on the machine. |
| **Why selected** | Standard; the same image runs on Apple silicon and Linux CI (pinned multi-arch digest). |
| **Invoked by** | `npm run db:*` (`docker compose --env-file .env.local …`), the Supabase CLI, the web template's `db` tests (unique Compose projects on random loopback ports), `e2e.mjs`. |
| **Consumes / produces** | `compose.yaml`, `.env.local` → container `db`, named volume `<project>_db-data`. |
| **Phase** | Development, CI (template `database` job), release (acceptance). |
| **Caveats** | **Volumes outlive containers and keep the password they were initialized with**: a fresh `db:init` against an old volume fails authentication (`28P01`). Docker Desktop publishes ports on all interfaces by default, which matters for Supabase. |

## PostgreSQL 17

| | |
|---|---|
| **Problem** | The application's data store, sessions store and authorization engine (row-level security). |
| **Why selected** | One data model for both providers; RLS and roles are PostgreSQL features, so authorization does not depend on a vendor. |
| **Invoked by** | The application (`pg` as `app_runtime`), migrations and tests (as owner). |
| **Phase** | Runtime, development, CI (`postgres:17.10` service in generated CI). |
| **Caveats** | Local only in this baseline: the migration tool refuses a non-local host unless `MIGRATE_ALLOW_REMOTE=true`. |

## Supabase CLI 2.122.1

| | |
|---|---|
| **Problem** | A local Supabase-compatible stack for projects that plan to host on Supabase. |
| **Why selected** | Supabase is treated as a **PostgreSQL and local-services provider**, not a different architecture. The CLI is an exact-pinned npm dev dependency, so no global install. |
| **Invoked by** | `npm run db:*` (`npx --no-install supabase start|stop|status|migration up|migration list --local`). |
| **Consumes** | `supabase/config.toml`, `supabase/migrations/`. |
| **Phase** | Development, release. |
| **Caveats** | Supabase Auth, Studio, Storage, Realtime and others are **disabled**; the Data API exposes only `public` and `graphql_public`, so the app's `app` and `app_auth` schemas are not reachable through it. Ports are published on all interfaces with documented default keys: `db:up` fails closed unless `SUPABASE_ALLOW_LAN_EXPOSURE=true`. Creates `supabase/.temp` and `.branches`. Recommended ≥ 7 GB memory for the full stack. |

## Better Auth 1.7.16

| | |
|---|---|
| **Problem** | Email/password authentication with database sessions, CSRF/origin protection and rate limiting, on any PostgreSQL. |
| **Why selected** | Runs directly on PostgreSQL through `pg`, so **one authentication system serves both providers**. Supabase Auth was rejected: two session mechanisms, two authorization models and application code that would need to know its provider (`developer-platform/docs/architecture.md`, "Decision: Better Auth on PostgreSQL"). |
| **Invoked by** | `src/server/auth/auth.ts` (`createAuth`), mounted at `/api/auth/[...all]`; `withAuthentication` and `requirePrincipal` for `/api/v1`. |
| **Consumes** | `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, trusted origins, the `pg` pool; tables in `app_auth` created by committed migrations. |
| **Produces** | Session cookies (browser), signed `set-auth-token` headers (bearer plugin, native clients), session rows. |
| **Phase** | Runtime. |
| **Caveats** | No runtime schema migration; `schema.db.test.ts` fails if a version needs more schema. Telemetry disabled. Cookie cache disabled (sessions read from the DB on every request). Needs `.npmrc` `legacy-peer-deps=true`. Email verification and password-reset delivery are not configured (no mail service). |

## Migration tooling (`scripts/db/migrations.mjs`)

| | |
|---|---|
| **Problem** | Ordered, immutable, verifiable SQL migrations shared by both providers. |
| **Why selected** | Plain SQL, no ORM lock-in; the directory follows the Supabase CLI's convention so the same files serve both. |
| **Produces** | `public.schema_migrations` (postgres provider); a per-file SHA-256 lock in `supabase/migrations.lock/`. |
| **Caveats** | One lock file per migration, so two branches adding migrations never conflict; on Supabase the CLI applies the files and keeps its own history (`supabase_migrations.schema_migrations`). |
