# PostgreSQL, Supabase and migrations

`database` (template 0.5.0+) is **one choice**: `none` (default), `postgres` or `supabase`. Both providers are PostgreSQL 17 and run the **same migrations, data layer and authentication**. The difference is only local tooling.

## Provider mode

| | `postgres` | `supabase` |
|---|---|---|
| Local service | `compose.yaml`: `postgres:17.10@sha256:7958…3317`, port on `127.0.0.1` only, named volume, health check, `no-new-privileges` | `supabase/config.toml`: the Supabase CLI's local stack (PostgreSQL 17 on 54322, Data API on 54321) |
| Started by | `docker compose up --detach --wait` | `npx --no-install supabase start` |
| Credentials | random password generated into `.env.local` by `db:init` | the CLI's documented local defaults (`postgres`/`postgres`) |
| Migration runner | `scripts/db/migrations.mjs` (bookkeeping in `public.schema_migrations`) | `supabase migration up` (history in `supabase_migrations.schema_migrations`) |
| Extra dependency | none | `supabase` CLI 2.122.1 (npm dev) |
| Network exposure | loopback only | the CLI publishes on all interfaces; `db:up` fails closed unless `SUPABASE_ALLOW_LAN_EXPOSURE=true` |
| Supabase services | – | Auth (GoTrue), Studio, Storage, Realtime, Edge Runtime, SMTP, Analytics **disabled** |
| Data API | – | exposes only `public` and `graphql_public`; `app` and `app_auth` are not reachable; the migration revokes everything from `anon`, `authenticated`, `service_role` |

**Supabase is a provider, not an architecture.** The application never uses the Supabase client, Supabase Auth, its JWTs or its Data API for application data. A future provider only has to be PostgreSQL to inherit the model.

**Changing provider is not an upgrade.** `devkit upgrade --set database=<other>` is refused (sticky). To switch: generate a new project with the other provider, move migrations and data deliberately (`pg_dump`/`psql`), verify. Application code in `src/` does not change.

## Migrations

```text
supabase/
├── migrations/
│   ├── 20260101000000_create_items.sql            # app schema, app.items
│   ├── 20260301000000_create_auth.sql             # app_runtime role, app_auth schema, Better Auth tables
│   └── 20260301000100_scope_items_to_owner.sql    # owner_id, RLS policies, column grants
└── migrations.lock/
    └── <same names>.sha256                        # one checksum file per migration
```

- **One canonical history for both providers** (the directory follows the Supabase CLI convention).
- File names: `<14-digit version>_<lowercase_name>.sql`, applied in version order, each in its own transaction (no `begin`/`commit` in the file; no `create index concurrently`).
- **Never edit a committed migration.** `npm run db:verify` and a test in `npm run check` fail on an edited, renamed, deleted or unlocked migration. The postgres runner additionally refuses an applied migration whose checksum changed and a new migration older than an applied one.
- One `.sha256` per migration, so two branches adding migrations never conflict.
- Better Auth's tables are not created at run time: they are committed SQL, and `schema.db.test.ts` fails if a Better Auth version would want more.
- A data-preserving change (renaming a column) is a new migration that moves the data.

## Server-only data access

```text
src/server/db/
├── config.ts        # validated env: DATABASE_URL / DATABASE_RUNTIME_URL, pool max 1–20 (5), timeouts
├── pool.ts          # one pg.Pool per server process; statement and idle-in-transaction timeouts
├── transaction.ts   # withTransaction(tx => …): COMMIT on return, ROLLBACK on throw
├── errors.ts        # DatabaseError with a code; never the SQL, parameters, URL or row data
└── index.ts
src/server/items/
├── repository.ts    # parameterized SQL over app.items; Zod-validated input and output
└── http.ts          # (auth) maps repository results to API responses
```

Rules (from the generated `docs/database.md` and `AGENTS.md`):

- Every module starts with `import "server-only"`.
- **Parameterized SQL only**; column names come from fixed lists, never from callers.
- Validate at the boundary: repository functions parse input with `src/lib/schemas/item.ts` and return validated objects; invalid input throws `DatabaseError("invalid_input")` before SQL runs.
- Errors are classified: `not_found`, `conflict`, `constraint_violation`, `invalid_input`, `timeout`, `unavailable`, `unexpected`; safe to log or map to a problem.
- Everything is bounded: connect, statement and idle-in-transaction timeouts; list at most 100 rows.
- With `auth`, every repository function takes an **owner scope** from `withPrincipal`; route handlers never import the pool or `withTransaction` (a test enforces it). See [Authorization](authorization.md).

## Connections

| Variable | Role | Used by |
|---|---|---|
| `DATABASE_URL` | the owner (administrative) | migrations, `db:*`, tests, tools; **never** the running app (with auth) |
| `DATABASE_RUNTIME_URL` | `app_runtime` | the running application |

Both are server-only; never give one a `NEXT_PUBLIC_` name.

## Tests

- `npm run check` (no database): configuration, error classification, schemas, migration files and lock, server-only boundaries.
- `npm run test:db`: CRUD, missing records, invalid input, SQL-injection attempts, duplicates and constraints, transactions, timeouts, connection failures, the migration runner; with auth, the whole auth and RLS suite. Each test file creates and drops **its own** database, refuses a non-local server, and never touches your development data. 70 tests in the acceptance run.
- Generated CI's `database` job: a `postgres:17.10` service container with `trust` auth (reachable only from that job), `npm run db:verify`, `npm run test:db`.
