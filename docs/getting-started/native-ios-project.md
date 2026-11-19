# A native iOS project

The `native-ios` profile is `full-stack` with `native_client` fixed on, **plus a second template layer** that adds a SwiftUI app in `ios/`. You still choose the database provider.

## 1. Generate both layers

```bash
uv run devkit new field-notes --profile native-ios --set database=postgres \
  --native-set bundle_identifier=com.example.fieldnotes \
  --native-set release_api_host=api.example.com \
  --output-dir ..
```

`--native-set` options (all optional; defaults are placeholders):

| Option | Default | Meaning |
|---|---|---|
| `app_display_name` | title-cased `app_name` | name under the icon (≤ 30 ASCII letters, digits, spaces) |
| `bundle_identifier` | `com.example.<app_name without hyphens>` | reverse DNS; choose yours before signing for a device |
| `debug_api_port` | `3000` | Debug build talks to `http://localhost:PORT` |
| `release_api_host` | `api.example.com` | Release build talks to `https://HOST` |

What happens (details in [Generation flow and atomicity](../architecture/generation-flow.md)):

1. Both templates are resolved to release tags (web `v0.7.1`, native `v0.1.1`) and the pair is checked against `NATIVE_REQUIRES_WEB` (native 0.1.x needs web `>=0.7.0,<0.8.0`).
2. The web layer is rendered into a hidden staging directory `../.field-notes.devkit-partial`.
3. The native layer is rendered into the same staging directory.
4. Only when both succeeded is the staging directory renamed to `../field-notes`.

```text
Native iOS layer: https://github.com/audiophreak/native-ios-template.git @ v0.1.1

Created .../field-notes

Next steps:
  cd .../field-notes
  git init && git add -A && git commit -m 'chore: initial commit'
  npm ci
  npm run check
  npm run db:init && npm run db:up && npm run db:migrate   # then `npm run test:db`
  open ios/App.xcodeproj    # Xcode 26+; or: sh ios/scripts/test.sh
  node ios/scripts/e2e.mjs  # the real end-to-end scenario on the simulator
Read AGENTS.md (web) and ios/AGENTS.md (iOS). The two layers upgrade separately: `devkit status`.
```

## 2. Commit and check both layers

```bash
cd ../field-notes
git init -b main && git add -A && git commit -m "chore: initial commit"
uv run --project ~/Developer/developer-platform devkit status .
```

```text
web     v0.7.1    up to date
native  v0.1.1    up to date
```

Two answers files now exist: `.copier-answers.yml` (web, records `native_client: true`) and `.copier-answers.ios.yml` (native, records `_src_path`, `_commit: v0.1.1` and the `--native-set` answers).

## 3. Web gates

```bash
npm ci
npm run check            # 257 tests in the acceptance run (includes the OpenAPI drift test)
npm run db:init && npm run db:up && npm run db:migrate
npm run test:db
```

## 4. Native gates

From `ios/`:

```bash
cd ios
sh scripts/check-static.sh        # source rules (no ATS exceptions, no token in UserDefaults, ...)
sh scripts/check-contract.sh      # Contract/openapi.json == ../openapi/openapi.json, checksum matches
sh scripts/check-generated.sh     # regenerate the Swift client into a temp dir; require zero diff
(cd Packages/AppCore && swift test)   # 58 package tests on the Mac host
sh scripts/test.sh                # hosted app tests (11) + package tests (58) on the iOS Simulator
sh scripts/check-release-config.sh    # Release build: https only, no App Transport Security entry
```

Pick a simulator with `IOS_SIMULATOR="iPhone 17"` (a name or UDID); otherwise the first available iPhone is used.

## 5. Run the app

```bash
cd ..                               # project root
AUTH_ALLOW_SIGN_UP=true npm run dev # the Debug build talks to http://localhost:3000
open ios/App.xcodeproj              # choose an iPhone simulator, Run, then "Create an account"
```

## 6. The real end-to-end scenario

```bash
node ios/scripts/e2e.mjs            # add --down to stop the database afterwards (volume kept)
```

It builds and starts the web app (`next start`) on a free loopback port with open sign-up, creates two throwaway accounts with random passwords, and runs `ios/AppTests/EndToEndTests.swift` on the simulator in two phases:

1. sign in, token stored in the Keychain, session, create/read/update, a second account is refused another user's item;
2. **after restarting the web server and the database**: relaunch still signed in, delete, sign out, the old token now gets `401`.

It checks the server log contains no authorization header or token. This is a **local release gate**, not a CI job, because GitHub's macOS runners do not reliably provide Docker. See [Release gates and acceptance](../testing/release-gates.md).

## Adding the native layer later

A full-stack project can gain the native layer later. Each step is reviewed and committed separately:

```bash
devkit native add PROJECT                       # refused until native_client is on:
# error: The web part has to serve native clients first: run `devkit upgrade PROJECT --set native_client=true` ...
devkit upgrade PROJECT --set native_client=true
git -C PROJECT add -A && git -C PROJECT commit -m "feat: serve native clients"
devkit native add PROJECT                       # adds only ios/ and .copier-answers.ios.yml
git -C PROJECT add -A && git -C PROJECT commit -m "feat: add the native iOS layer"
```
