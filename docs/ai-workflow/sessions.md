# Sessions, prompts and review

## Session continuity

Agent sessions end; the work must not depend on what a session remembers. Continuity lives in files:

| Artifact | Purpose |
|---|---|
| `developer-platform/docs/NEXT_SESSION.md` | "Read this first": where each repository is, published vs proposed versions, branches and PRs, exact test results at the checkpoint, unresolved decisions, the release sequence, the commands to resume, the next recommended task. Updated at the end of each work package. |
| `CHANGELOG.md` (each repository) | what each release changed, written for upgraders |
| `docs/milestone-*.md`, `docs/release-strategy.md` | decision records and incident analyses |
| release tags | the only definition of "released" |
| CI evidence artifacts | what actually ran on which commit |

A new session starts by reading `AGENTS.md` (automatic through `CLAUDE.md`), then `NEXT_SESSION.md`, then verifying the state it describes (`git status`, `git log`, `gh pr checks`, tags) rather than trusting it.

!!! note "Handoff files may contain local paths"
    `NEXT_SESSION.md` says so itself: it is a handoff for the owner and contains local paths on purpose; generalize them before any repository is made public. It contains no credentials.

## Prompt design (work packages)

The later releases were built as numbered work packages (the handoff and the acceptance scripts refer to WP3, authentication, and WP4, native iOS). A work-package prompt that works well here states:

1. **Objective** in terms of observable outcomes (a release, a feature with its gate).
2. **Authorized repositories** and, explicitly, the read-only ones.
3. **Authoritative sources**: the released tags, not earlier descriptions.
4. **Required gates** with exact commands and what "pass" means (counts, no skips).
5. **Publication rules**: what may be committed, pushed or tagged, and in which order (template first).
6. **Stop conditions**: when to stop and ask (architecture, dependencies, anything destructive, an ambiguous requirement).
7. **The report expected**: actual results, SHAs, failures, open questions.

Avoid prompts that describe a desired implementation in detail while leaving the gates vague; the gates are what make an agent's work checkable.

## Implementation versus independent review

The agent that implemented a change is the worst judge of it. The practice on this platform:

- **Implementation session**: plans, implements on a branch, runs the gates, reports actual output.
- **Independent review**: a separate session (or reviewer) reads the diff against the stated objective, re-runs the gates itself, and looks for what the implementer had reason not to see: weakened tests, swallowed errors, scope creep, undocumented behaviour changes, secrets in output.
- **Acceptance**: a fail-closed audit against the **published** tags, generating fresh projects from GitHub, asserting exit codes and parsed counts, and proving unauthorized repositories were untouched. The 151-gate audit is the model ([Release gates](../testing/release-gates.md)).

A finding goes back to implementation; nothing is "accepted with a note".

## Regression testing

- Every behaviour change carries a test; tests are never weakened to pass (`ios/AGENTS.md` says so explicitly).
- Incidents become tests: the destructive-command lint (with the incident command as a negative control), the strict-boolean tests (`zod=banana`), the numeric `_commit` Prettier test, the stale-volume preflight gate.
- Byte identity (`compare_release.py`) proves a feature-off release did not regress existing projects.
- Upgrade tests start from the **real published tags**, so a regression in the upgrade path is caught against what users actually have.

## Lint, type-check and build gates

| Repository | The gate an agent must pass before saying "done" |
|---|---|
| developer-platform | `uv run pytest` (and `-m integration` before a release) |
| web-core-template | `uv run pytest` (full, including e2e); `-m db` for database/auth changes |
| native-ios-template | `uv run pytest` (including `xcode`) |
| generated web project | `npm run check` (lint, typecheck, format, tests, build); `npm run test:db` for data/auth |
| generated iOS layer | `sh ios/scripts/test.sh` plus the `check-*` scripts |

## Branches, PRs and releases

1. Branch from `main` (`feat/…`, `fix/…`, `chore/…`).
2. Commit in coherent steps with conventional prefixes.
3. Push and open a PR (draft while incomplete; the body states "do not merge or tag" until approved).
4. CI green on every matrix entry; evidence downloaded if needed.
5. Owner approves; merge with a **merge commit**.
6. CI green on the merge commit; annotated tag; verify the remote tag and privacy.
7. Order across repositories: web template → native template → platform → acceptance.

## Avoiding changes outside authorized repositories

- Name the authorized repositories in the prompt; name the read-only ones too (the reference app `my-first-app` has always been read-only).
- Generate and experiment in **fresh scratch workspaces** (`tools/scratch.py new`, `mktemp -d`), never inside a source checkout (`devkit new` refuses destinations inside the checkouts anyway).
- End every work package by proving the untouched repositories are untouched: `git -C REPO status --porcelain`, `git rev-parse HEAD`, tags and branches unchanged (three gates of the acceptance audit do exactly this).
- Run `devkit` from the platform checkout with `uv run --project …` rather than installing it anywhere.
