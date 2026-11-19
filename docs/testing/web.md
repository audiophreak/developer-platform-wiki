# Web and generated-project tests

## Inside every generated project

### `npm run check` (no services needed)

| Test area | Files (feature) | Proves |
|---|---|---|
| UI | `src/app/page.test.tsx`, `src/components/ui/button.test.tsx` | the scaffold renders |
| Schemas | `src/lib/schemas/*.test.ts` (zod) | accepted and rejected input tables |
| Forms | `example-form.test.tsx`, `forms-example/page.test.tsx` (forms) | accessible errors, resolver wiring (jsdom) |
| Handlers | `src/app/api/v1/**/route.test.ts`, `src/server/api/*.test.ts` (rest_api) | status, body, headers, size and media-type limits; handlers called with a `Request`, no server |
| API contract | `src/lib/schemas/v1/contract.test.ts`, `auth-contract.test.ts` | every field name and error code pinned (additive-only v1) |
| Server boundary | `src/server/boundary.test.ts`, `src/server/*/server-only.test.ts` | client components cannot reach `src/server`; schemas free of framework/env/DB imports |
| Migrations | `scripts/db/migrations.test.ts` (database) | files valid and locked; edits detected |
| Auth config | `src/server/auth/config.test.ts`, `guard.test.ts` (auth) | secret rules, origins, the guard's 401/403 decisions |
| **OpenAPI drift** | `src/lib/openapi/document.test.ts`, `src/server/api/openapi-contract.test.ts` (native_client) | committed contract == generated; route coverage; `bearerAuth` on protected routes; documented statuses == handler statuses; list bounds == Zod |

Plus lint, `tsc`, Prettier and a production `next build`.

### `npm run test:db` (real PostgreSQL)

Each `*.db.test.ts` file creates and drops its own throwaway database on the server in `DATABASE_URL`, refuses a non-local server, and runs as the real `app_runtime` role (`set role app_runtime`) where authorization matters.

| Area | Files | Proves |
|---|---|---|
| Connection layer | `src/server/db/connection.db.test.ts` | pool, timeouts, connection failures, error classification |
| Repository | `src/server/items/repository.db.test.ts` (without auth) | CRUD, not found, invalid input, injection attempts, duplicates, constraints, transactions |
| Migration runner | `scripts/db/migrations.db.test.ts` | ordering, idempotence, checksum and order refusals, rollback of a failed migration |
| **Authentication** | `src/server/auth/auth.db.test.ts` | sign-up, sign-in, wrong credentials, hashing, sessions, sign-out, revocation, expiry, password change, real `Set-Cookie` attributes, origin checks, rate limits |
| **Authorization** | `src/server/auth/authorization.db.test.ts`, `src/app/api/v1/items/route.db.test.ts` | runtime role privileges; RLS with and without a user; cross-user 404; one pooled connection and many concurrent users; every protected route |
| Schema parity | `src/server/auth/schema.db.test.ts` | Better Auth's own tooling would create nothing more after the migrations |

70 tests passed per project in the acceptance run, on both providers.

## In the web-core-template repository

`uv run pytest` (919 collected) drives Copier, npm and Docker as subprocesses:

| Marker / file | Proves |
|---|---|
| `test_render.py`, `test_answer_types.py`, `test_copier_answers_formatting.py` | rendering, strict booleans, answer validation, no secrets/identities/paths in output, no `_tasks`/`_migrations` |
| `test_features.py`, `test_lock_matrix.py` | feature registry ↔ validators parity; every valid configuration renders and receives the lock `features.py` names; locks additive, registry-only, no install scripts; matrix ≤ 16 |
| `test_*_feature.py` | each feature's files, prerequisites and rejections |
| `test_upgrade.py`, `test_*_upgrade.py`, `test_versioned_source.py` | upgrades **from the real published tags** keep selections and user edits; enabling features later; invalid input fails safely |
| `test_compare_release.py` | byte identity with the previous release |
| `-m e2e` (32), `test_e2e.py` | generate apps across feature combinations, `npm ci` + `npm run check` + production `npm audit` in each, evidence recorded |
| `-m db` (109): `test_database_postgres.py`, `test_database_supabase.py`, `test_auth_database*.py`, `test_native_client.py` | the whole feature against **real PostgreSQL and a real local Supabase stack** through a production server: providers, migrations, LAN-exposure guard, auth flows, bearer tokens (signature enforcement, forged tokens, rotation on password change, revocation), provider equivalence |
| `test_no_destructive_commands.py`, `test_ci_workflow.py` | no banned commands; CI evidence and scanning intact |

Each `db` test uses a unique Compose project or Supabase project id on random loopback ports and removes its containers and volumes (scoped by that unique name) at the end. In CI they **fail** rather than skip if Docker is missing.

## In developer-platform

`uv run pytest` (503) uses small **fixture templates in temporary Git repositories** (`tests/fixtures/mini_template`) so versioned sources, an https-style origin, upgrades, unavailable templates, existing destinations, failed generation, staging and the native layer need no published repository. `test_contract_snapshots.py` checks the registry against every snapshot offline. `-m integration` (28) is the live gate against the real template checkouts.
