# Better Auth operations

Better Auth **1.7.16** (exact pin, `auth` feature) has no CLI in these projects: its schema is committed SQL and nothing alters the database at run time. Operations are HTTP calls to its own endpoints under `/api/auth`, configuration in `.env.local`, and the project's `db:*` scripts.

## Configuration

| Variable | Set by | Notes |
|---|---|---|
| `BETTER_AUTH_SECRET` | `npm run db:init` (random 32 bytes, hex) | ≥ 32 characters, not repetitive; **no default exists**: authentication refuses to start without a valid one. Rotating it signs everyone out. |
| `BETTER_AUTH_URL` | `db:init` (`http://localhost:3000`) | The exact origin in the browser's address bar; `https` unless loopback. `localhost` ≠ `127.0.0.1`. |
| `AUTH_TRUSTED_ORIGINS` | you | Extra origins, comma separated, no wildcards; `https` in production. |
| `AUTH_ALLOW_SIGN_UP` | you | Default: on outside production, **off in production**. |
| `AUTH_TRUSTED_IP_HEADER`, `AUTH_TRUSTED_PROXIES` | you | Only behind your own proxy; otherwise rate limits share one bucket per route. |
| `DATABASE_RUNTIME_URL` | `db:init` | The `app_runtime` connection the application uses. |

## Account and session operations

All are `POST` with `content-type: application/json`. From a browser, an `Origin` header must be trusted. Native clients send **no** `Origin` and no cookie.

```bash
BASE=http://localhost:3000
# sign up (requires AUTH_ALLOW_SIGN_UP=true, or the non-production default); 12-128 character password
curl -i -X POST $BASE/api/auth/sign-up/email -H 'content-type: application/json' -H "origin: $BASE" \
  -d '{"email":"me@example.test","password":"a long local passphrase","name":"Me"}'
# sign in: browser gets Set-Cookie; a bearer client reads the set-auth-token header
curl -i -X POST $BASE/api/auth/sign-in/email -H 'content-type: application/json' -H "origin: $BASE" \
  -d '{"email":"me@example.test","password":"a long local passphrase"}'
# who am I (the application's own endpoint, never returns a token)
curl -b 'better-auth.session_token=…' $BASE/api/v1/session
curl -H 'authorization: Bearer <set-auth-token value>' $BASE/api/v1/session    # native_client projects
# list my sessions (no tokens) / end one / sign out / change password
curl -b '…' $BASE/api/v1/sessions
curl -b '…' -H "origin: $BASE" -H 'content-type: application/json' -X POST $BASE/api/auth/revoke-session -d '{"token":"…"}'
curl -b '…' -H "origin: $BASE" -X POST $BASE/api/auth/sign-out
curl -b '…' -H "origin: $BASE" -H 'content-type: application/json' -X POST $BASE/api/auth/change-password \
  -d '{"currentPassword":"…","newPassword":"…","revokeOtherSessions":true}'
```

Rate limits (stored in the database): sign-in, sign-up and password change 3 per 10 s; reset/verification 3 per minute; everything else 60 per minute. A `429` means wait.

## Database-side operations

```bash
npm run db:migrate      # schema + app_runtime password
npm run db:roles        # app_runtime password only (after `supabase db reset`, or if 28P01 for app_runtime)
npm run db:status       # shows the runtime role's attributes, never its password
```

```sql
-- assign items created before auth existed (administrative connection)
update app.items set owner_id = '<user id>' where owner_id is null;
-- inspect sessions (administrative connection)
select "userId", "expiresAt", "createdAt" from app_auth."session" order by "createdAt" desc limit 20;
```

## Upgrading Better Auth

From `web-core-template/docs/features.md`: bump the exact pin in `template/package.json.jinja`, regenerate the locks (`tools/refresh_locks.py`), review the added packages, and let `src/server/auth/schema.db.test.ts` decide whether a new migration is needed (it asks Better Auth's own schema tooling what it would still create and requires the answer to be nothing). Read the release notes; never skip the Docker tests. Template 0.6.1 was exactly such a release (1.7.15 → 1.7.16, 12 advisories reviewed as not exploitable in the generated configuration).

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `Invalid authentication configuration: check BETTER_AUTH_SECRET` | missing, short or placeholder secret | `npm run db:init` (appends it) |
| `The application database role must not be an owner or an administrator` | `DATABASE_RUNTIME_URL` points at the owner | use the `app_runtime` URL, `npm run db:migrate` |
| `password authentication failed for user "app_runtime"` | role has no password yet, or it changed | `npm run db:roles` |
| `403 origin_not_allowed` on sign-in or writes | `Origin` not trusted | make `BETTER_AUTH_URL` match the address bar |
| `401 unauthenticated` with a bearer token | token unsigned, revoked, expired, or rotated by a password change | sign in again; adopt any `set-auth-token` |
