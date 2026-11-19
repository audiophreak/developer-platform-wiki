# Database: Docker, PostgreSQL, Supabase

Generated projects with `database=postgres` or `database=supabase` drive their database through `npm run db:*` (`scripts/db/cli.mjs`). That file is the **only** provider-specific code; application code under `src/` does not know which provider runs.

## The project commands

| Command | `postgres` provider | `supabase` provider |
|---|---|---|
| `npm run db:init` | Writes `.env.local` (mode 0600): `POSTGRES_USER=app`, a random `POSTGRES_PASSWORD`, `POSTGRES_DB=app`, `POSTGRES_PORT` (default 5432), `DATABASE_URL`. With `auth`: `DATABASE_RUNTIME_URL` (user `app_runtime`, random password), `BETTER_AUTH_SECRET` (random), `BETTER_AUTH_URL=http://localhost:3000`. | `DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres` (the CLI's documented local defaults), plus the same auth lines. |
| `npm run db:up` | `docker compose --env-file .env.local up --detach --wait` | `npx --no-install supabase start`, then the LAN-exposure check (stops the stack if ports are published beyond loopback, unless `SUPABASE_ALLOW_LAN_EXPOSURE=true`) |
| `npm run db:down` | `docker compose … down` (volume kept) | `supabase stop` (data kept) |
| `npm run db:status` | `docker compose ps`, applied/pending counts from `public.schema_migrations`, runtime role | exposure, `supabase status`, `supabase migration list --local`, runtime role |
| `npm run db:logs` | last 100 lines of the `db` service | not available (use Docker's tools) |
| `npm run db:migrate` | verifies the lock, refuses a non-local host (unless `MIGRATE_ALLOW_REMOTE=true`), applies pending migrations in their own transactions, then provisions `app_runtime` | verifies the lock, `supabase migration up` (local), then provisions `app_runtime` |
| `npm run db:verify` | offline lock check | same |
| `npm run db:lock` | record new migrations' SHA-256 in `supabase/migrations.lock/` | same |
| `npm run db:roles` | (auth) set `app_runtime`'s password from `DATABASE_RUNTIME_URL` | same; also needed after `npx supabase db reset` |
| `npm run test:db` | real-database Vitest suite; each file creates and drops its own throwaway database on the server in `DATABASE_URL`, refuses a non-local server | same |

`db:init` on an existing `.env.local`: without auth it changes nothing; with auth it **appends only missing lines** and never changes a value.

!!! danger "No command deletes data, on purpose"
    To discard a local PostgreSQL database completely, run `docker compose --env-file .env.local down --volumes` yourself, knowing it deletes the named volume. For Supabase, `npx supabase db reset` recreates the local database from migrations and discards data. Never point either at anything remote.

## Docker and Docker Compose

```bash
docker info                                         # daemon reachable?
docker compose --env-file .env.local ps             # this project's services
docker compose --env-file .env.local logs --tail 100 db
docker volume ls                                    # named volumes (<project>_db-data)
docker ps --filter label=com.supabase.cli.project=<app_name>   # the Supabase stack's containers
```

The generated `compose.yaml` runs one `db` service: `postgres:17.10` pinned by multi-arch digest, port published on **`127.0.0.1` only**, a named volume `db-data`, `no-new-privileges`, and a `pg_isready` health check (so `up --wait` returns when the database accepts connections). Credentials come only from `.env.local`; the file contains no secret and fails with `run npm run db:init` if a variable is missing.

## PostgreSQL

```bash
# a psql shell inside the container (postgres provider)
docker compose --env-file .env.local exec db psql -U app app

# a backup (keep it out of git)
docker compose --env-file .env.local exec db pg_dump -U app app > backup.sql

# Supabase provider: psql against the stack
psql postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

Useful queries when diagnosing:

```sql
select version, checksum from public.schema_migrations order by version;      -- postgres provider history
select rolname, rolsuper, rolcreaterole, rolcreatedb, rolbypassrls, rolcanlogin
  from pg_roles where rolname = 'app_runtime';                                -- the runtime role
select * from pg_policies where schemaname = 'app';                            -- row-level security policies
```

## Supabase CLI

Version **2.122.1**, a dev dependency of Supabase-provider projects. Always via `npx --no-install supabase` (or `npm run db:*`):

```bash
npx --no-install supabase start
npx --no-install supabase status
npx --no-install supabase migration list --local
npx --no-install supabase migration up
npx --no-install supabase stop
npx --no-install supabase db reset        # destructive: local only
```

The generated `supabase/config.toml` enables only the database (port 54322, PostgreSQL 17) and the Data API gateway (port 54321, exposing only `public` and `graphql_public`). Auth, Studio, Storage, Realtime, Edge Runtime, local SMTP and Analytics are **disabled**. The first `start` downloads images and needs several GB of memory.

**Lifecycle files.** The CLI creates `supabase/.temp` and `supabase/.branches` on first start. Templates from 0.6.0 ignore them; older Supabase projects must add both to `.gitignore` before their first upgrade.

## Migrations

```text
supabase/migrations/20260101000000_create_items.sql
supabase/migrations/20260301000000_create_auth.sql            # auth
supabase/migrations/20260301000100_scope_items_to_owner.sql   # auth
supabase/migrations.lock/<same names>.sha256
```

Add a migration (never edit a committed one):

```bash
$EDITOR supabase/migrations/20261201093000_add_notes.sql   # a version later than every existing one
npm run db:lock
npm run db:migrate
npm run test:db
```

**Failure modes:** `was modified after it was locked` / `after it was applied` (restore the original from Git; put your change in a new migration); `is older than the newest applied migration` (choose a later version); a failed migration is rolled back entirely and nothing is recorded.
