# Acceptance evidence

The manual's acceptance claims (151 / 151, 177 / 177, 192 / 192) rest on the evidence files archived here, in `docs/evidence/` of this private repository. They were produced on the owner's workstation by a **fail-closed acceptance harness** and copied here so the claims can be checked without that workstation.

## Runs

| Run | Combination tested | Result | Evidence file | Written (UTC, file time) |
|---|---|---|---|---|
| Original baseline, run 1 | devkit v0.8.0, web v0.7.0, native v0.1.0 | 143 / 149 (6 failed) | [`run1-wp4-audit.tsv`](../evidence/2026-11-19-original-baseline/run1-wp4-audit.tsv) | 2026-11-19 14:13 |
| Original baseline, run 2 | same | 135 / 149 (14 failed) | [`run2-wp4-audit.tsv`](../evidence/2026-11-19-original-baseline/run2-wp4-audit.tsv) | 2026-11-19 14:20 |
| **Original baseline, run 3 (accepted)** | same | **151 / 151** | [`run3-wp4-audit-ACCEPTED.tsv`](../evidence/2026-11-19-original-baseline/run3-wp4-audit-ACCEPTED.tsv) | 2026-11-19 14:28 |
| **Native v0.1.1 patch (accepted)** | devkit v0.8.0, web v0.7.0, native v0.1.1 | **177 / 177** | [`native-v0.1.1-audit-ACCEPTED.tsv`](../evidence/2026-11-19-native-v0.1.1/native-v0.1.1-audit-ACCEPTED.tsv) | 2026-11-19 18:14 |
| **Documentation closeout (accepted, current)** | devkit v0.8.1, web v0.7.1, native v0.1.1 | **192 / 192** | [`closeout-v0.8.1-audit-ACCEPTED.tsv`](../evidence/2026-11-19-closeout-v0.8.1/closeout-v0.8.1-audit-ACCEPTED.tsv) | 2026-11-19 20:26 |

Runs 1 and 2 are kept because they show the harness failing closed on real problems (an over-strict skip detector and stale Docker volumes; see [Release gates](../testing/release-gates.md#how-acceptance-was-reached)); they are not acceptances.

## What each file establishes

Each TSV has one line per gate, `PASS|FAIL <tab> project <tab> gate <tab> detail`, and a last line `TOTAL gates N passed P failed F`. From the files alone:

- **Versions tested:** the first gates of every run assert the remote annotated tag of each repository resolves to the expected commit (the SHA is in the detail column), that `main` equals it, that the repository is **PRIVATE**, and that `main` CI is green on that SHA; the platform is cloned at its tag and `devkit --version` is checked (`devkit 0.8.1` in the closeout run); generated projects' `.copier-answers*.yml` provenance is checked against the published release tags.
- **Individual outcomes:** every gate's verdict, with exit codes and parsed counts in the detail column (for example `Swift Testing 58 passed (expected 58), no unexpected skips`, `70 tests passed … none failed or skipped`).
- **Totals:** the last line (for example `TOTAL gates 192 passed 192 failed 0`).
- **That nothing else was touched:** the final gates prove the three source repositories' HEAD, status, tags and branches were unchanged by the run.

## How the harness fails closed

From the archived harness (each run's `*.sanitized.py`):

- Every gate is one subprocess run from an argument list (no shell, no pipes); its exit code is asserted, and its output is checked where a count or marker matters (no failed, skipped or todo tests; expected Swift Testing totals; e2e markers).
- A gate that fails is recorded and the run continues, so every problem is reported; gates that depend on a failed project are recorded as **BLOCKED**, which is also a failure.
- A command that cannot start, or times out, is a failure, never a pass.
- The process exits 0 only if every gate passed; the evidence file is written either way.
- Preflight: Docker reachable with no containers, and no leftover volumes that would reuse an old database password (the closeout run scopes this to its own `co-` project names and deletes nothing).

## Context the evidence does and does not contain

| Available in the evidence | Not in the evidence (not claimed) |
|---|---|
| exact commits and tags of all three repositories, privacy, CI status | Xcode, macOS, Node, Docker or simulator versions used by the run |
| devkit version (from `devkit --version`), `devkit doctor` passing | wall-clock start and end of each gate (only the file's write time above) |
| per-project test counts and e2e markers | the simulator model (the harness is given a simulator UDID; it is not recorded) |

The run date is the evidence files' write time on 2026-11-19. Toolchain facts quoted elsewhere in this manual (for example Xcode 27.2 on the acceptance workstation) come from separate observation, not from these files.

## Provenance and integrity

- The harnesses ran from the owner's `~/Claude` directory against fresh `tools/scratch.py` workspaces and wrote their TSVs to `~/Claude/audit-evidence/`. The TSVs are archived **verbatim**.
- The harnesses are archived as **sanitized copies**: the only change is that one literal in the personal-data scan pattern (the owner's surname) is replaced with `OWNER-SURNAME-REDACTED`. The SHA-256 of each executed original is recorded, so a copy kept elsewhere can be matched.
- No evidence file contains credentials, passwords, tokens or personal paths. The harness prints none, and `scripts/check_content.py` scans this directory in CI.
- Checksums: [`SHA256SUMS`](../evidence/SHA256SUMS). Verify with:

```bash
cd docs/evidence && grep -v '^#' SHA256SUMS | grep -v 'original:' | shasum -a 256 -c
```

| File | SHA-256 |
|---|---|
| `2026-11-19-original-baseline/run3-wp4-audit-ACCEPTED.tsv` | `10603edb618d7896b5cfde2b129b6965fbf845b3a01977e33acf0d76e6d350b3` |
| `2026-11-19-native-v0.1.1/native-v0.1.1-audit-ACCEPTED.tsv` | `fda2ca3310d68f09092e1376a5990294a6d0bc5c2dd30fa3c219465d9050e598` |
| `2026-11-19-closeout-v0.8.1/closeout-v0.8.1-audit-ACCEPTED.tsv` | `e7247536614438426be7c4db0c7ceed3b1d0c0a4eecd22a5faa938a966d89f04` |
| original `audit-wp4.py` (151-gate harness) | `6f448b150712778b88efc6d69d36802b049a4af1874d0983a5a760007fddaeff` |
| original `audit-native-v0.1.1.py` (177-gate harness) | `447c227be936c939349d426f6f634bcc67c5cc12de75afbc70a0370a67ada0cd` |
| original `audit-closeout-v0.8.1.py` (192-gate harness) | `73b7797123b29b2bc94b1f12c3f74b40acc8c056747c9ba201ef80f24bbe4aa2` |

## CI negative controls (probe branches)

Separate from acceptance, the CI evidence workflows of `developer-platform` and `web-core-template` were proven on 2026-11-17 to report a deliberate failure correctly:

| Repository | Probe commit | Pull request | CI run | Result |
|---|---|---|---|---|
| developer-platform | `8a3b8d1333c389b857c24dea03729589ce62c438` | #3 (closed, not merged) | `44118456812` | failure on 3.12 and 3.14, as intended |
| web-core-template | `e451b938fa2f5e2a9e6f059101c5f22942a34eda` | #3 (closed, not merged) | `44118473632` | failure on 3.12 and 3.14, as intended |

Each commit added `tests/test_zz_ci_probe.py` with one deliberately failing and one deliberately skipped test. They remain reachable on GitHub through the closed pull requests (`refs/pull/3/head`), and each repository's `docs/ci-evidence.md` (from devkit v0.8.1 and web v0.7.1) records them. The local `probe/ci-evidence-failure` branch refs were removed in the closeout after this record existed.
