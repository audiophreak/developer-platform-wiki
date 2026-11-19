# Xcode and the Simulator

Most native failures are environment failures: the toolchain, a simulator runtime or CoreSimulator's services, not the project. Always establish a known-good simulator first:

```bash
xcodebuild -version && xcode-select -p
xcrun simctl list runtimes
UDID="$(sh ios/scripts/simulator.sh)" && echo "$UDID"
xcrun simctl boot "$UDID" || true
xcrun simctl bootstatus "$UDID" -b          # returns when fully booted
```

## Xcode version compatibility

**Symptoms.** `doctor`: `[warn] xcode 16.x (the native-ios profile needs 26+)`; Swift 6 strict-concurrency or iOS 17 API errors (`@Observable`, `ContentUnavailableView`) when building; `xcode-select: error: tool 'xcodebuild' requires Xcode, but active developer directory '/Library/Developer/CommandLineTools' is a command line tools instance`; `You have not agreed to the Xcode license agreements`.

**Likely cause.** Xcode older than 26; the active developer directory points at the Command Line Tools or at a different Xcode; the license was never accepted after an install or update.

**Diagnostics.**

```bash
xcodebuild -version
xcode-select -p                                   # /Applications/Xcode.app/Contents/Developer
ls -d /Applications/Xcode*.app
swift --version
```

**Safe recovery.**

```bash
sudo xcode-select -s /Applications/Xcode.app      # or the Xcode you intend to use
sudo xcodebuild -license accept
sudo xcodebuild -runFirstLaunch
```

The template targets **Xcode 26+**. The native template's CI selects the newest installed Xcode 26 on `macos-26`; the acceptance workstation ran Xcode **27.2** successfully. A newer major is expected to work but is not what CI tests; if a build fails only on a newer Xcode, reproduce on Xcode 26 before changing code.

**Evidence.** *Repository source* (`doctor.py` `MIN_XCODE_MAJOR = 26`, native CI); Xcode 27.2 on the acceptance workstation.

## `xcodebuild -runFirstLaunch`

**Symptoms.** After installing or updating Xcode: `xcodebuild` asks to install additional components; simulator services fail to start; `CoreSimulator is out of date`; builds fail in system frameworks; test runs fail before any test starts.

**Likely cause.** Xcode's first-launch packages (system resources, CoreSimulator, device support) are not installed for this Xcode. Opening Xcode's GUI once also does this, but command-line-only use skips it.

**Diagnostics.** `xcodebuild -checkFirstLaunchStatus; echo $?` (non-zero means first-launch tasks are pending).

**Safe recovery.** `sudo xcodebuild -runFirstLaunch`, then quit Simulator and any `xcodebuild` processes, and retry. Repeat after **every** Xcode update.

**Evidence.** *Owner-reported*; recommended in [Prerequisites](../getting-started/prerequisites.md#6-xcode-and-the-ios-simulator).

## Simulator runtime management

**Symptoms.** `no iPhone simulator is installed (Xcode > Settings > Components)` from `simulator.sh`; `no available simulator matches IOS_SIMULATOR=…`; `doctor`: `no iOS Simulator runtime`; `Unable to find a destination matching the provided destination specifier`; devices marked `(unavailable, runtime profile not found)`.

**Likely cause.** No iOS runtime installed (runtimes are separate downloads), a runtime that does not match the installed Xcode's SDK, or a device created for a runtime since removed. Disk space for runtime images.

**Diagnostics.**

```bash
xcrun simctl list runtimes
xcrun simctl runtime list                    # installed runtime images and their state
xcrun simctl list devices available
df -h /                                      # runtime images are several GB
```

**Safe recovery.** Install a runtime from **Xcode › Settings › Components** (or `xcodebuild -downloadPlatform iOS`). Create a dedicated device rather than reusing a damaged one:

```bash
xcrun simctl create "Platform iPhone" "iPhone 17" "$(xcrun simctl list runtimes | awk '/^iOS/{id=$NF} END{print id}')"
export IOS_SIMULATOR="Platform iPhone"
```

Removing unavailable devices (`xcrun simctl delete unavailable`) is optional housekeeping and only affects devices that can no longer run.

**Evidence.** *Repository source* (`simulator.sh`, `doctor.py` messages); *owner-reported* for runtime mismatches.

## XCTest runner hangs

**Symptoms.** `xcodebuild test` sits for minutes, then: `The test runner hung before establishing connection`, or `Timed out while launching / waiting for the test runner`, or the run ends with `** TEST FAILED **` and zero tests executed.

**Likely cause.** The handshake between `xcodebuild` and the test runner process on the simulator stalls: the simulator was still booting, CoreSimulator's service is in a bad state after an Xcode update or sleep, or the host app failed to launch (see SpringBoard below).

**Diagnostics.**

```bash
xcrun simctl list devices booted
xcrun simctl bootstatus "$UDID" -b
pgrep -fl CoreSimulatorService
ls -t ~/Library/Logs/DiagnosticReports | head      # recent crash reports
```

**Safe recovery.**

1. Boot and wait **before** testing: `xcrun simctl boot "$UDID"; xcrun simctl bootstatus "$UDID" -b`, then `sh ios/scripts/test.sh app`.
2. Reset the simulator processes: quit Simulator.app, `xcrun simctl shutdown all`, retry.
3. For the **package** tests, bypass the handshake: `sh ios/scripts/test.sh direct` (builds for testing, then runs the `.xctest` bundle with the simulator's own `xctest` via `simctl spawn`). The hosted app tests have no such bypass; fix the simulator.
4. If it persists after an Xcode update: `sudo xcodebuild -runFirstLaunch`, log out and in (restarts CoreSimulator cleanly), or use a freshly created device.

**Evidence.** *Repository source*: `ios/scripts/test.sh` documents `direct` mode for exactly this message.

## `DTServiceHubClient failed to bless service hub`

**Symptoms.** This line appears in `xcodebuild` output, sometimes alone (and tests pass), sometimes alongside a runner hang or a failure to launch the app on the simulator.

**Likely cause.** `DTServiceHub` is Xcode's developer-tools service broker, launched and authorized ("blessed") on demand for debugging and device/simulator services. The message means that launch or authorization failed. Typical triggers: Xcode's first-launch components missing after an update; `xcodebuild` run from a context without a full user session (SSH, some automation sandboxes) where the authorization cannot be granted; a stale service from a previous Xcode version still running.

**Diagnostics.**

```bash
xcodebuild -checkFirstLaunchStatus; echo $?
DevToolsSecurity -status                    # developer-tools access for this user
pgrep -fl DTServiceHub
xcode-select -p
```

**Safe recovery.** First decide whether it matters: if tests ran and `** TEST SUCCEEDED **` follows, it is noise. Otherwise: `sudo xcodebuild -runFirstLaunch`; run from a normal logged-in Terminal session (not over SSH); make sure only one Xcode is active (`xcode-select -p`); quit Xcode and Simulator, `xcrun simctl shutdown all`, and retry; as a last resort log out and in. Do not disable security features to silence it.

**Evidence.** *Owner-reported.* The repositories do not record this message; the explanation is based on Xcode's documented components and should be treated as a working diagnosis.

## Simulator SpringBoard and PosterBoard failures

**Symptoms.** The simulator shows a black or frozen home screen, or repeatedly restarts it; `bootstatus` never completes; hosted tests fail with the app failing to launch (`Application failed to launch`, `The request to open "<bundle id>" failed`); crash reports for `SpringBoard` or `PosterBoard` in `~/Library/Logs/DiagnosticReports`.

**Likely cause.** SpringBoard (the simulator's home screen and app launcher) or PosterBoard (the lock-screen/wallpaper poster service in recent iOS) crashing in that simulator's data container, typically a device whose state was created by an older runtime or interrupted mid-boot. Hosted tests need SpringBoard to launch the host app, so they cannot run.

**Diagnostics.**

```bash
xcrun simctl spawn "$UDID" log show --last 10m \
  --predicate 'process == "SpringBoard" OR process == "PosterBoard"' | tail -50
ls -t ~/Library/Logs/DiagnosticReports | grep -Ei 'springboard|posterboard' | head
xcrun simctl list devices | grep "$UDID"
```

**Safe recovery.**

1. `xcrun simctl shutdown "$UDID"`, then boot and wait again.
2. Prefer a **new** device (non-destructive): `xcrun simctl create …` and `export IOS_SIMULATOR=…` (see runtime management above).
3. If you want to keep the device name: `xcrun simctl erase "$UDID"` wipes **that simulator's** data (apps, Keychain, settings). Nothing in the project depends on simulator data; the tests create what they need.
4. Make sure the runtime matches the Xcode in use.

**Evidence.** *Owner-reported.* Not recorded in the repositories; the acceptance runs used a healthy simulator selected by UDID (`IOS_SIMULATOR`).

## Keychain error -34018

**Symptoms.** A Keychain call fails with `AppError.storage(-34018)`; `errSecMissingEntitlement` in logs; Keychain tests fail only when run outside the app.

**Likely cause.** The code ran in a process with **no application entitlements**, so it has no Keychain access group: an unhosted test bundle (`swift test`, the package scheme) or a host app that did not launch. That is precisely why `KeychainTokenStoreTests` live in `ios/AppTests` (hosted by the app) and not in the package.

**Diagnostics.**

```bash
grep -rn KeychainTokenStoreTests ios/AppTests ios/Packages/AppCore/Tests
sh ios/scripts/test.sh app
```

**Safe recovery.** Run Keychain tests through `sh ios/scripts/test.sh app`, never as package tests; do not move them into `Packages/AppCore/Tests`. If they fail with `-34018` even hosted, the host app did not launch properly: fix the simulator (SpringBoard section above). Never work around it by storing the token somewhere else; `check-static.sh` forbids UserDefaults and files for credentials.

**Evidence.** *Repository source*: the comment at the top of `ios/AppTests/KeychainTokenStoreTests.swift`. See [why the tests are hosted](../ios/testing.md#why-the-keychain-tests-must-be-hosted).

## Upgrade refused after running the iOS checks

Only projects still on native **v0.1.0**: see [Copier, Git and CI](git-copier-ci.md#upgrade-refused-after-running-the-ios-checks). Fixed in v0.1.1.
