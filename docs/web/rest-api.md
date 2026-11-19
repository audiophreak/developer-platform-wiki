# REST API and problem details

`rest_api` (template 0.4.0+) adds a versioned JSON API under `/api/v1`, implemented as Next.js route handlers, with shared Zod contracts and RFC 9457 errors. It adds **no npm dependency**.

## Endpoints at v0.7.0

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| GET | `/api/v1/app-info` | public | 200 `AppInfo` | 405 |
| POST | `/api/v1/examples/validate` | public | 200 `ValidateExampleResponse` | 400, 405, 413, 415, 422 |
| GET | `/api/v1/session` | session | 200 `SessionResponse` | 401, 405 |
| GET | `/api/v1/sessions` | session | 200 `SessionListResponse` (no tokens) | 401, 405 |
| GET | `/api/v1/items?limit=&offset=` | session | 200 `ItemListResponse` (limit 1–100, default 20) | 401, 405, 422 |
| POST | `/api/v1/items` | session | 201 `ItemResponse` + `Location` | 400, 401, 403, 405, 413, 415, 422 |
| GET | `/api/v1/items/{id}` | session | 200 `ItemResponse` | 401, 404, 405 |
| PATCH | `/api/v1/items/{id}` | session | 200 `ItemResponse` | 400, 401, 403, 404, 405, 413, 415, 422 |
| DELETE | `/api/v1/items/{id}` | session | 204 | 401, 403, 404, 405 |
| any | any other `/api/v1/…` | – | – | 404 |

An item is `{ id, title, body, createdAt, updatedAt }`; title 1–100 characters and unique per owner (case-insensitive), body ≤ 2000. Responses never contain the owner id, a password hash, a session token, connection details or exceptions. Other methods on a known path return 405 with `Allow`. No response carries CORS headers.

## Request handling

`src/server/api/request.ts` (`readJson`) enforces, while streaming: `Content-Type: application/json` (415 + `Accept-Post`), a body of at most **8 KiB** (413), valid UTF-8 and JSON (400 `invalid_json`). The handler then `safeParse`s with the request schema (422 `validation_failed`). Requests are **strict**: unknown fields are rejected.

## RFC 9457 problem details

Every error is `application/problem+json`:

```json
{
  "type": "urn:problem-type:validation_failed",
  "title": "The request is not valid",
  "status": 422,
  "code": "validation_failed",
  "errors": [{ "path": "title", "message": "Title is required" }]
}
```

| Status | `code` |
|---|---|
| 400 | `invalid_json` |
| 401 | `unauthenticated` |
| 403 | `origin_not_allowed` |
| 404 | `not_found` |
| 405 | `method_not_allowed` |
| 413 | `payload_too_large` |
| 415 | `unsupported_media_type` |
| 422 | `validation_failed` (with `errors`, at most 10) |
| 500 | `internal_error` |

Clients branch on **`code`**, never on `title`. A problem never contains a stack trace, file path, secret or submitted value. Handlers build them with `problem(code)` from `src/server/api/responses.ts`, and wrap their body in `guarded(...)` so any thrown error becomes the generic 500.

## Versioning

- The version is in the path. Within `v1`, changes are **additive only**: new endpoints, new optional request fields, new response fields, new error codes. Nothing is renamed, removed, made required or tightened.
- A breaking change creates `/api/v2` beside `v1`; `v1` is retired only after a published deprecation window, because native apps cannot be force-updated.
- `src/lib/schemas/v1/contract.test.ts` pins every field name and error code, so an accidental break fails `npm run check`.
- With `native_client`, response schemas **allow unknown fields** and the problem `code` is an open string with known values as `examples`, so a generated client does not fail on a value added within v1. Requests remain strict.

## Adding an endpoint

1. Write the request/response schemas in `src/lib/schemas/v1/` and a test.
2. Write the handler in `src/app/api/v1/…/route.ts`: `readJson` → `safeParse` → work → `json(schema, data)` or `problem(code)`. Wrap protected handlers in `withAuthentication` and reach data only through `withPrincipal`.
3. Add a handler test that calls the handler with a `Request` (no server needed).
4. With `native_client`: add the operation to `src/lib/openapi/document.ts`, run `npm run openapi:generate`, commit the contract; in a native project, `sh ios/scripts/sync-contract.sh`.
5. `npm run check` (and `npm run test:db` if it touches data).
