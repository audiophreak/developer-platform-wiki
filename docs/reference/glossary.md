# Glossary

answers file
:   The YAML file Copier writes into a project recording the template origin (`_src_path`), the release rendered (`_commit`) and every answer. `.copier-answers.yml` for the web layer, `.copier-answers.ios.yml` for the native layer. Commit it; never edit it.

`app_runtime`
:   The least-privilege PostgreSQL role the running application connects as (`DATABASE_RUNTIME_URL`). No superuser, no role/database creation, no RLS bypass, owns nothing, column-level grants.

bearer token
:   The signed Better Auth session token (`token.signature`) sent as `Authorization: Bearer …` by native clients. Same session as the browser cookie.

contract (platform)
:   What `devkit` depends on in a template release: its questions (types, defaults, choices) and Node major. Snapshotted in `tests/contracts/`.

contract (API)
:   `openapi/openapi.json`, the OpenAPI 3.1 description of `/api/v1`, generated from the Zod schemas; copied into `ios/Contract/` for the Swift client.

`.devkit-partial`
:   The hidden staging directory `.NAME.devkit-partial` used by two-layer generation; left in place on failure for inspection.

fixed option
:   An option a profile defines (for example `auth=true` in `full-stack`). May be repeated, never contradicted.

layer
:   One Copier template applied to a project directory with its own answers file. Native projects have a web layer and a native layer.

live release gate
:   `pytest -m integration` in `developer-platform`: compares snapshots with the real template checkouts. Local only.

local mode
:   `devkit new --template PATH`: renders a template checkout as it is on disk, for template development; records a home-relative path.

lock matrix
:   The set of committed lockfiles in `web-core-template/locks/`, one per distinct npm dependency set (11 at v0.7.0), selected by the computed `lock_key`.

`NATIVE_REQUIRES_WEB`
:   The registry table of which web releases each native release works with (native 0.1.x ↔ web `>=0.7.0,<0.8.0`).

owner scope
:   The handle `withPrincipal` gives a repository: a transaction in which `app.user_id` is set for exactly one user.

principal
:   The authenticated identity issued by `src/server/auth/principal.ts` after a valid session; cannot be constructed from a user id.

problem details
:   RFC 9457 error documents (`application/problem+json`) with a stable `code`.

profile
:   A named composition of a template (and optionally a native layer) with fixed and required options: `web-core`, `full-stack`, `native-ios`.

published mode
:   The default: render the profile's GitHub origin at a supported release tag; records the URL and tag.

release gate
:   A check that must pass before tagging but does not run in CI.

required option
:   An option a profile requires you to state, because it is an architectural choice (`database` in `full-stack` and `native-ios`).

RLS
:   Row-level security: PostgreSQL policies on `app.items` restricting rows to `owner_id = app.current_user_id()`.

`since`
:   The first template release that has an option; `devkit` refuses an option for older releases.

staging
:   Building into `.NAME.devkit-partial` and renaming into place only when every layer succeeded.

sticky option
:   An option `devkit upgrade` will not change once set to a non-default value: `database`, `auth`, `native_client`.

strict boolean
:   A Copier question written as `type: yaml` + `choices: [false, true]` + an `is boolean` validator, so non-boolean input is rejected.

supported range
:   The half-open range of template releases a `devkit` version accepts, e.g. `>=0.1.0,<0.8.0`.
