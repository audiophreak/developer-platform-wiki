# Docker, PostgreSQL, Supabase

## Stale Docker volumes and 28P01

**Symptoms.** `npm run db:migrate` → `error: cannot connect to the database (28P01)`; then `test:db` fails in its teardown (`database.drop()`), and `e2e.mjs` fails with `db:migrate failed`. `db:up` itself succeeded.

**Likely cause.** `28P01` is PostgreSQL's `invalid_password`. The official image applies `POSTGRES_PASSWORD` **only when it initializes an empty data directory**. A named volume (`<project>_db-data`) left from an earlier project with the same Compose project name still holds the database initialized with the **old** password, while a fresh `npm run db:init` wrote a **new** random password into `.env.local`. Compose reuses the volume; the passwords disagree.

**Diagnostics.**

```bash
docker volume ls                                     # look for <project>_db-data from earlier runs
docker compose --env-file .env.local ps
grep -c POSTGRES_PASSWORD .env.local                 # present (never print it)
docker compose --env-file .env.local logs --tail 30 db   # "password authentication failed for user \"app\""
```

**Safe recovery.** Choose one, deliberately:

- **Keep the data:** restore the `.env.local` that created the volume (from your own backup; it is not in Git).
- **Discard the local data:** `docker compose --env-file .env.local down --volumes` (deletes this project's named volume), then `npm run db:up && npm run db:migrate`.

Prevention: before a fresh run with reused project names, check `docker volume ls` for leftovers. The final acceptance audit gained exactly this preflight gate ("no leftover docker volumes (stale volumes keep old passwords)").

**Evidence.** *Acceptance runs*: run 2 failed 14 gates with `cannot connect to the database (28P01)` in both postgres projects; *repository source*: the generated `docs/database.md` troubleshooting ("Authentication fails after a fresh db:init. The volume still holds the earlier password").

## PostgreSQL authentication failures

| Symptom | Cause | Diagnose | Recover |
|---|---|---|---|
| `password authentication failed for user "app"` (28P01) | stale volume (above), or `.env.local` edited | `docker volume ls`, compose logs | above |
| `password authentication failed for user "app_runtime"` | the role has no password yet (fresh migrate interrupted), it changed, or after `supabase db reset` | `npm run db:status` (role attributes) | `npm run db:roles` |
| `The application database role must not be an owner or an administrator` | `DATABASE_RUNTIME_URL` points at the owner | compare user in both URLs (never print them whole) | use the `app_runtime` URL `db:init` wrote; `npm run db:migrate` |
| auth fails though passwords look right | **another PostgreSQL on port 5432** (Homebrew `postgresql`, Postgres.app) answers instead of the container | `lsof -nP -iTCP:5432 -sTCP:LISTEN` | stop the other server, or `POSTGRES_PORT=55432` before `db:init` (or edit the port in `.env.local` and `DATABASE_URL`) |
| `refuses a database that is not local` | `DATABASE_URL` host not loopback | – | by design; `MIGRATE_ALLOW_REMOTE=true` only if you really mean it |
| `DATABASE_URL is not set` / `.env.local does not exist` | `db:init` not run | – | `npm run db:init` |

**Evidence.** *Repository source* (`docs/auth.md`, `docs/database.md`, `cli.mjs`); the port-conflict row is *owner-reported*.

## Supabase lifecycle issues

| Symptom | Cause | Recover |
|---|---|---|
| `db:up`: `error: the local Supabase stack is reachable from other machines … the stack was stopped` | the CLI publishes ports on all interfaces with documented default keys; `db:up` fails closed (data kept) | make Docker publish on loopback (Docker Desktop › Settings › Docker Engine: `"ip": "127.0.0.1"`), or on a fully trusted network `SUPABASE_ALLOW_LAN_EXPOSURE=true npm run db:up` |
| first `db:up` very slow or out of memory | images download; the stack wants memory (Supabase recommends ≥ 7 GB) | wait; raise Docker's memory; the template disables unused services |
| `port 54321/54322 already allocated` | another Supabase project is running | `npx supabase stop` in that project, or change ports in `supabase/config.toml` and `.env.local` |
| `npx: … supabase … missing packages` | running `npx supabase` outside a Supabase-provider project or before `npm ci` | `npm ci` in the project; always `npx --no-install supabase` |
| upgrade refused: untracked `supabase/.temp`, `supabase/.branches` | the CLI creates them on first start; pre-0.6.0 templates did not ignore them | add both to `.gitignore`, commit, upgrade |
| `db:status` reported `applied: 0, pending: 1` though applied (template 0.5.0) | it read the postgres runner's table, absent on Supabase | fixed in 0.5.1 (shows `supabase migration list`); upgrade |
| `app_runtime` login fails after `npx supabase db reset` | the reset recreates the role without the password | `npm run db:roles` |

`npm run db:status` on Supabase first prints `network exposure: loopback only` or `REACHABLE FROM OTHER MACHINES`.

**Evidence.** *Repository source* (`cli.mjs`, template `CHANGELOG.md` 0.5.1 and 0.6.0, `docs/database.md`). The acceptance audit ran with `SUPABASE_ALLOW_LAN_EXPOSURE=true` on the owner's workstation.

## Docker in general

```bash
docker info > /dev/null || echo "daemon not reachable: start Docker Desktop or OrbStack"
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
docker system df                                    # disk used by images, containers, volumes
```

Template `db` tests and the acceptance audit name every Compose project and Supabase project id uniquely and remove only their own containers and volumes, scoped by that name. Never run a global prune to "fix" a project: it deletes other projects' data.
