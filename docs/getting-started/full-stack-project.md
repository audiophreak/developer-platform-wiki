# A full-stack project

The `full-stack` profile is Web Core with **`zod`, `rest_api` and `auth` fixed on**, plus a database provider **you must choose**. `forms` stays optional.

## 1. Choose the provider and generate

=== "PostgreSQL in Docker Compose"

    ```bash
    uv run devkit new shop --profile full-stack --set database=postgres --output-dir ..
    ```

=== "Local Supabase stack"

    ```bash
    uv run devkit new shop --profile full-stack --set database=supabase --output-dir ..
    ```

Both providers run **the same application code, migrations and authentication** (Better Auth on PostgreSQL). The provider only changes local tooling. See [PostgreSQL, Supabase and migrations](../web/database.md) for the difference.

!!! warning "The provider is permanent for the project"
    `database` is a *sticky* option: once a project has `postgres` or `supabase`, `devkit upgrade --set database=...` with another value is refused (exit 2). Moving data between providers is not automated.

What `devkit` refuses, and why:

```text
$ uv run devkit new shop --profile full-stack
error: Profile 'full-stack' needs an explicit choice for database (devkit never picks an architecture for you): add --set database=postgres or --set database=supabase.

$ uv run devkit new shop --profile full-stack --set database=postgres --set auth=false
error: Profile 'full-stack' sets auth=true; --set auth=false contradicts it. Use another profile instead.
```

## 2. Commit and validate without a database

```bash
cd ../shop
git init -b main && git add -A && git commit -m "chore: initial commit"
npm ci
npm run check
```

`npm run check` needs **no database**: database tests are named `*.db.test.ts` and excluded from it. The acceptance run recorded **248 tests** passing in a full-stack project.

## 3. Start the database and run the real-database tests

```bash
npm run db:init     # .env.local (mode 0600, git-ignored): random DB password, app_runtime password, BETTER_AUTH_SECRET
npm run db:up       # postgres: docker compose up + health wait;  supabase: local stack via the pinned CLI
npm run db:migrate  # applies supabase/migrations/*.sql, then gives app_runtime its password
npm run db:status   # containers + "3 migrations applied, none pending" + runtime role attributes
npm run test:db     # 70 real-database tests in the acceptance run
```

`db:init` never overwrites an existing `.env.local`; on an existing file it only appends missing lines. There is **no command that deletes data**; `npm run db:down` stops containers and keeps the volume.

!!! note "Supabase LAN exposure check"
    The Supabase CLI publishes its ports on all interfaces with documented default credentials. `npm run db:up` inspects what Docker published and **stops the stack (keeping data)** if other machines could connect, unless `SUPABASE_ALLOW_LAN_EXPOSURE=true`. Prefer configuring Docker to publish on `127.0.0.1`.

## 4. Run and sign up

```bash
AUTH_ALLOW_SIGN_UP=true npm run dev
```

Open sign-up is on by default outside production, off in production. From another terminal:

```bash
curl -i -X POST http://localhost:3000/api/auth/sign-up/email \
  -H 'content-type: application/json' -H 'origin: http://localhost:3000' \
  -d '{"email":"me@example.test","password":"a long local passphrase","name":"Me"}'
```

The response sets the `better-auth.session_token` cookie (`HttpOnly`, `SameSite=Lax`). Send it to the protected API:

```bash
curl -b 'better-auth.session_token=<value from Set-Cookie>' http://localhost:3000/api/v1/session
curl -b '...' -H 'content-type: application/json' -H 'origin: http://localhost:3000' \
     -X POST -d '{"title":"First item"}' http://localhost:3000/api/v1/items
```

Without a session, `/api/v1/items` answers `401` with an RFC 9457 problem whose `code` is `unauthenticated`.

## 5. What was added

```text
shop/
├── .env.example               # names and placeholders only
├── .npmrc                     # legacy-peer-deps=true (matches how the lock was produced)
├── compose.yaml               # postgres provider only: postgres:17.10@sha256:..., 127.0.0.1 port, named volume
├── supabase/
│   ├── config.toml            # supabase provider only: Auth, Studio, Storage, Realtime disabled
│   ├── migrations/            # canonical SQL history for both providers
│   └── migrations.lock/       # one .sha256 per migration (edits are detected)
├── scripts/db/                # cli.mjs (db:*), migrations.mjs (runner + lock), roles.mjs (app_runtime)
├── docs/                      # api-v1.md, database.md, auth.md: read these
├── vitest.db.config.mts       # test:db configuration
└── src/
    ├── app/api/auth/[...all]/ # Better Auth handler
    ├── app/api/v1/            # app-info, examples/validate, session, sessions, items, items/[id], 404 catch-all
    ├── lib/schemas/           # Zod schemas shared by client and server (v1/ = API contracts)
    ├── lib/auth-client.ts     # the only auth module a browser may import
    └── server/                # server-only: api/, db/, items/, auth/
```

Read the generated `docs/auth.md` before exposing anything: the project is ready for local development and integration testing, **not for open registration on the public internet** (no mail service, no email verification, trusted-proxy and origin settings are the deployer's).

## 6. Stop

```bash
npm run db:down     # containers stop; data is kept
```
