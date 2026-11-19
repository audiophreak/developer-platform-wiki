# Testing and Release transport

## Where each native test runs

| Suite | Location | Runner | Count | What it covers |
|---|---|---|---|---|
| Package tests (host) | `Packages/AppCore/Tests/AppCoreTests` | `swift test` on macOS | 58 | problem details, configuration, auth state machine, middleware, auth service, API service (including malformed and unexpected answers), models, contract compatibility, a whole-scenario test against a stand-in server |
| Package tests (simulator) | same | `sh scripts/test.sh package` (`xcodebuild test -scheme AppCore-Package`) | 58 | the same tests on the iOS runtime |
| Hosted app tests | `AppTests/` | `sh scripts/test.sh app` (`xcodebuild test -scheme App`) | 11 | Keychain (5), build configuration (3), end-to-end (3, enabled only when `e2e.mjs` sets `E2E_PHASE`) |
| Release configuration | built Release `Info.plist` | `sh scripts/check-release-config.sh` | – | `APIScheme` = https, no `NSAppTransportSecurity` key, configured host |
| Static rules | sources | `sh scripts/check-static.sh` | – | no ATS opt-out, no trust override, no logged token, no credentials in UserDefaults/files, no hard-coded http URL, no secrets or team IDs |
| Contract and client | `Contract/`, `Sources/APIClient` | `check-contract.sh`, `check-generated.sh` | – | checksum, equality with the web contract, zero-diff regeneration |
| End-to-end | `AppTests/EndToEndTests.swift` | `node scripts/e2e.mjs` | 2 phases | real web server, real database, real Better Auth, the simulator |

The package's tests use `InMemoryTokenStore` and a stand-in server (no network); the Keychain implementation is tested only in the hosted target.

## Why the Keychain tests must be hosted

The iOS Keychain is per-application: an item belongs to an access group derived from the app's **entitlements and signature**. A test bundle run by itself (an unhosted XCTest/Swift Testing process, which is what `swift test` and the package scheme produce) has no application, no entitlements and so no Keychain access group. Every `SecItem*` call there fails with **`-34018` (`errSecMissingEntitlement`)**.

So `KeychainTokenStoreTests` lives in `ios/AppTests`, the test target **hosted by the app**: the tests are injected into the running `App` process on the simulator and inherit its Keychain context. The file says so itself:

> These run inside the app on the iOS Simulator (they are in the app's test target, hosted by the app): an unhosted test process has no Keychain entitlement and every call fails with -34018.

What the hosted Keychain tests prove:

1. nothing stored reads as `nil`;
2. save, read, **replace** (a rotated token replaces rather than duplicates), delete, and deleting what is not there is not an error;
3. the stored item is device-local, unlocked-only (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly`) and not synchronizable;
4. two services do not see each other's token;
5. the token is not in `UserDefaults` or the app's preference files.

Each test uses its own service name (`tests.<UUID>`) and removes what it stored. If you ever see `-34018` in a test run, a Keychain test is running unhosted, or the simulator's host app failed to launch (see [Xcode troubleshooting](../troubleshooting/xcode.md#keychain-error-34018)).

## Release HTTPS and App Transport Security

| | Debug | Release |
|---|---|---|
| `API_SCHEME` / `API_HOST` (xcconfig) | `http` / `localhost:<debug_api_port>` | `https` / `<release_api_host>` |
| `Info.plist` ATS | `NSAllowsLocalNetworking = true` only | **no `NSAppTransportSecurity` key at all**: the system default (https, valid certificates) applies |
| `APIConfiguration` | accepts http only for `localhost`, loopback, `*.local` | accepts **only https** (`#if DEBUG` decides) |
| Certificate validation | system | system; never disabled, never pinned |

Three independent checks keep Release honest: `check-release-config.sh` builds Release and inspects the built `Info.plist`; the hosted `BuildConfigurationTests` assert ATS is never disabled and the bundle carries no credential-looking value; `check-static.sh` forbids `NSAllowsArbitraryLoads`, `NSExceptionDomains`, `NSAllowsInsecureHTTPLoads` and trust overrides in source.

`release_api_host` defaults to the placeholder `api.example.com`: set the real host in `Config/Release.xcconfig` before shipping. Device signing (team, profile) is chosen in Xcode on your machine and is never committed.

## The end-to-end scenario

`node ios/scripts/e2e.mjs` is the only test that exercises the whole system: production web build, PostgreSQL (or Supabase), Better Auth, migrations, the runtime role, RLS, the bearer plugin, the generated client, the Keychain and the simulator. It restarts **both** the web server and the database between phases to prove the session and data survive. It is a local release gate because GitHub's macOS runners do not reliably provide Docker. In the accepted baseline it passed for both providers.
