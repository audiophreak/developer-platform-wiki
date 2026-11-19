# Native clients and the OpenAPI contract

`native_client` (template 0.7.0+, requires `auth`) makes the web application serve non-browser clients. It adds **no dependency** and changes only `src/server/auth/auth.ts`, one `package.json` script, `AGENTS.md`, `.prettierignore` and `eslint.config.mjs` (the last two learn to leave `ios/` alone), plus new files. With it off, every configuration is byte-identical to 0.6.1.

## Bearer support

```ts title="src/server/auth/auth.ts (native_client=true)"
plugins: [bearer({ requireSignature: true })],
```

- Better Auth's documented **bearer plugin** turns `Authorization: Bearer <token>` into the same session cookie before the session is read: one session table, one expiry, one revocation, one authorization model.
- `requireSignature: true`: the token must be the **signed** value (`token.signature`, exactly the cookie's value). A bare database token, a wrong signature or anything else is anonymous (`401 unauthenticated`).
- Native clients get the token from the **`set-auth-token`** response header of `POST /api/auth/sign-in/email` or `sign-up/email`, send **no** `Origin` and **no** cookie, and must adopt a new `set-auth-token` whenever a response carries one (a password change that revokes other sessions replaces the current session).
- The origin checks stay on: a request naming an untrusted origin is refused (403) with or without a token, so a web page cannot use a token even if it had one. The same rate limits apply.
- The token appears only in that header (and in Better Auth's own response bodies). `/api/v1` never returns it. Keep it in the Keychain; never in a URL, log, preference file or source.

No refresh-token scheme, device registry, social login or push notifications are included. A bearer session lasts as long as a browser session (7 days, refreshed on use).

## The deterministic OpenAPI 3.1 contract

`openapi/openapi.json` describes the API the application **owns** (`/api/v1`):

- 6 paths: `/api/v1/app-info`, `/api/v1/examples/validate`, `/api/v1/session`, `/api/v1/sessions`, `/api/v1/items`, `/api/v1/items/{id}`;
- request and response schemas, RFC 9457 problems with every stable `code`, the `bearerAuth` security scheme on protected operations, status codes and headers (`Location`, `Allow`, `Cache-Control`).

It is **generated, not written**: JSON Schema comes from the Zod schemas the handlers validate with (`z.toJSONSchema`, with `$ref`s between named schemas), and the operation list is `src/lib/openapi/document.ts`.

```bash
npm run openapi:generate      # writes, then verifies
```

`src/lib/openapi/document.test.ts` (inside `npm run check`, so also CI) fails when:

- the committed file differs from what the schemas generate (drift);
- a route has no operation, or an operation has no route;
- a protected route does not require `bearerAuth`, or a public one does;
- a documented problem status differs from what the handler sends;
- documented list bounds differ from the Zod schema.

**Determinism** is an acceptance gate: regenerating an unchanged project produces a byte-identical file, and the file is identical across both database providers (SHA-256 prefix `a42effbdb027d0c7`).

**Forward compatibility.** Response objects allow unlisted fields; the problem `code` is an open string with known values in `examples`. A generated client must not fail on a field or code added within v1. Requests stay strict.

**Boundary.** Better Auth's endpoints (`/api/auth/*`) are the library's documented behaviour and are **not** in the contract, so it does not drift with the library. Better Auth's early-stage OpenAPI plugin is not used. A native client calls those endpoints through a small, separately tested adapter (`AuthService` in the iOS app).

## Workflow when the API changes

```bash
# web part
$EDITOR src/lib/schemas/v1/items.ts src/app/api/v1/items/route.ts src/lib/openapi/document.ts
npm run openapi:generate
npm run check
# native part (native-ios projects)
sh ios/scripts/sync-contract.sh      # copy contract, record sha256, regenerate Swift client
sh ios/scripts/test.sh
git add openapi/ ios/Contract ios/Packages/AppCore/Sources/APIClient src/ && git commit
```

Removing `native_client` later is a hand-made code change (remove the plugin and the contract); `devkit upgrade --set native_client=false` is refused.
