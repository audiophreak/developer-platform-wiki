# Native tests

The native layer is tested at five levels. The design is in [Testing and Release transport](../ios/testing.md); this page is the operational view.

| Level | Command (from `ios/`) | Needs | CI | Acceptance result |
|---|---|---|---|---|
| Swift host tests | `(cd Packages/AppCore && swift test)` | Xcode toolchain | ✓ macOS job | 58 passed |
| Simulator package tests | `sh scripts/test.sh package` | Xcode + simulator runtime | ✓ macOS job | 58 passed |
| Hosted app + Keychain tests | `sh scripts/test.sh app` | Xcode + **booted, healthy simulator** | ✓ macOS job | 11 passed |
| Release HTTPS/ATS | `sh scripts/check-release-config.sh` | Xcode + simulator SDK | ✓ macOS job | passed |
| Static, contract, regeneration | `check-static.sh`, `check-contract.sh`, `check-generated.sh` | Xcode toolchain | ✓ macOS job | passed, zero diff |
| **Native e2e** | `node scripts/e2e.mjs` | Docker + Node 26 + web build + simulator, all at once | ✗ **local only** | passed, both providers |

## Running them in order

```bash
cd ios
export IOS_SIMULATOR="iPhone 17"           # optional: a name or UDID; default is the first available iPhone
sh scripts/check-static.sh
sh scripts/check-contract.sh
sh scripts/check-generated.sh
(cd Packages/AppCore && swift test)
xcrun simctl boot "$(sh scripts/simulator.sh)" || true
sh scripts/test.sh app
sh scripts/test.sh package
sh scripts/check-release-config.sh
cd .. && node ios/scripts/e2e.mjs --down
```

## When xcodebuild's test runner hangs

`sh scripts/test.sh direct` builds the package tests with `build-for-testing` and runs the `.xctest` bundle with the simulator's own `xctest` agent through `simctl spawn`, skipping the xcodebuild ↔ test-runner handshake that can stall with *"The test runner hung before establishing connection"*. It covers the package tests only; the hosted app tests need the normal path. See [Xcode troubleshooting](../troubleshooting/xcode.md#xctest-runner-hangs).

## In the native-ios-template repository

| Command | Tests | Proves |
|---|---|---|
| `uv run pytest -m "not xcode"` (38) | `test_render.py`, `test_update.py`, `test_dependencies.py` | answers validated; only `ios/` and its answers file are written (never a web file); no secrets, team ids, provisioning or home paths; static rules; dependency pins equal the documented table and are ≥ 14 days old; `copier update` of the layer alone |
| `uv run pytest -m xcode` (5) | `test_xcode.py` | the stale-contract check fails as designed; the generated client; `swift test`; `xcodebuild` on a simulator |
| `uv run python tools/gen_pbxproj.py --check` | | the committed Xcode project equals the generator's output |

CI runs `-m "not xcode"` on Ubuntu, and on `macos-26` renders the layer into a throwaway project and runs every script above except e2e, then `-m xcode`.

## Reading results

`xcodebuild test` prints `** TEST SUCCEEDED **` / `** TEST FAILED **` and Swift Testing's `Test run with N tests … passed`. Harmless noise you will see: `appintentsmetadataprocessor … warning: Metadata extraction skipped, no AppIntents.framework dependency found`. It is **not** a skipped test; an early acceptance run counted it as one and was fixed.
