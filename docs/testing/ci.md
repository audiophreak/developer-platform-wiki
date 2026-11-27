# GitHub CI versus local

## What runs where

| Check | GitHub CI | Local only | Why |
|---|:-:|:-:|---|
| Platform unit, safety, fixture-template tests | ✓ | | self-contained |
| Platform offline contract snapshots | ✓ | | snapshots replace cross-repo access |
| **Platform live gate** (`pytest -m integration`, 28) | skipped | ✓ | needs the template checkouts beside the platform; CI checks out only its own repository and holds no credential, by design |
| Web template render/feature/lock/upgrade tests | ✓ (3.12, 3.14) | | full history fetched so upgrades start from real tags |
| Web template e2e (npm in generated apps) | ✓ | | Node 26 on the runner |
| Web template real PostgreSQL + Supabase (`-m db`) | ✓ (`database` job, Docker required) | | Ubuntu runners have Docker |
| Native template render/layering/pins | ✓ (ubuntu-24.04) | | |
| Native template Xcode: client regeneration, `swift test`, simulator app + package tests, Release https | ✓ (macos-26) | | macOS runners have Xcode and simulators |
| **Native e2e** (`e2e.mjs`) | | ✓ | needs Docker **and** a simulator **and** a web build at once; macOS runners do not reliably provide Docker |
| Generated project `npm run check` | ✓ | | |
| Generated project `npm run test:db` | ✓ (`postgres:17.10` service) | | |
| Byte identity (`compare_release.py`), lock refresh check | (partly, via tests) | ✓ before tagging | release-time decisions |
| Published-pair acceptance (192 gates at the current baseline) | | ✓ | must use the **published** tags end to end, on a real workstation |

## Workflow conventions

Every workflow in the platform, web template and generated projects:

- triggers on push to `main` and on pull requests;
- `permissions: contents: read`;
- `actions/checkout` with `persist-credentials: false`;
- actions pinned to **full commit SHAs** with a version comment (`actions/checkout@3d3c42e5… # v7.0.1`, `setup-python@6d4fd22b… # v7.1.0`, `setup-node@949feb24… # v7.1.0`, `upload-artifact@cf430e03… # v7.0.2`);
- `uv` installed at an exact version (`pip install uv==0.13.6`), then `uv sync --locked`;
- no repository secrets.

The native template's workflow differs: it uses version tags (`actions/checkout@v4`, `astral-sh/setup-uv@v6`) rather than SHA pins, and a `concurrency` group that cancels superseded runs.

## CI evidence (platform and web template)

Every run, **including failed ones**, uploads `test-reports-py<version>-<commit>` (30 days):

| File | Contents |
|---|---|
| `junit.xml` | counts and every failure/error/skip with its reason; suite named `<repo>@<commit>-py<version>` |
| `pytest-output.txt` | the full console output |
| `metadata.txt` | `commit_under_test` (the PR head, not GitHub's synthetic merge), `github_sha`, run id, runner, Python/uv/pytest versions, `uv.lock` SHA-256 (web template: also Node, npm and lock hashes) |
| `installed-packages.txt` | `uv pip freeze` |
| `generated-apps/` (web template) | each e2e app's gate output and production `npm audit` |

Before upload, reports are scanned with a **quiet** `grep -q` for token shapes (GitHub tokens, private-key headers, AWS key ids); a hit fails the job without printing the match and skips the upload. A test fails if the workflow stops uploading on failure, drops the scan, widens the path, extends retention, adds a credential or dumps the environment.

```bash
gh run list --commit <sha>
gh run download <run-id> --dir "$(mktemp -d)"
```

Limits (from `docs/ci-evidence.md`): the scan protects the artifact, not the live log; it recognizes common shapes only; it is evidence, not attestation; tags are created by the maintainer, so "green before tag" is a process rule (rulesets protect `main` and make release tags immutable).

## Reading a red run

1. `gh run view <id> --log-failed`.
2. Download the artifact; read `junit.xml` failures and `metadata.txt` (is `commit_under_test` the commit you think?).
3. Reproduce locally with the same marker (`uv run pytest -m "not db"`, `-m db`, `-m xcode`).
4. Fix forward on the branch; never re-tag. See [Copier, Git and CI troubleshooting](../troubleshooting/git-copier-ci.md#ci-failures).
