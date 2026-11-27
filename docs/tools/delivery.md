# Delivery and AI tooling

## Git

| | |
|---|---|
| **Problem** | History, review, and the two mechanisms the platform's safety rests on: release tags and clean trees. |
| **Why selected** | Copier requires templates to be Git repositories whose tags are releases; `devkit upgrade` requires a clean, committed project so every upgrade is reversible. |
| **Invoked by** | You and agents; `devkit` (read-only: `ls-remote --tags`, `rev-parse`, `status --porcelain`, `show REF:copier.yml`) with `GIT_TERMINAL_PROMPT=0` and `GIT_OPTIONAL_LOCKS=0`; Copier (clone, diff, merge). |
| **Phase** | All. |
| **Caveats** | ≥ 2.27 (Copier). Published tags are immutable. Destructive commands are banned from code and docs by tests. |

## GitHub and the GitHub CLI

| | |
|---|---|
| **Problem** | Repository hosting, credentials for private template access, pull requests, CI results and evidence. |
| **Why selected** | `gh` stores the token in the keyring and can act as Git's credential helper (`gh auth setup-git`), so nothing secret enters a repository or a command line. |
| **Invoked by** | You (`gh repo create/clone`, `gh pr`, `gh run`), `doctor` (`gh auth status`), the acceptance audit (visibility, CI status). |
| **Phase** | Workstation, delivery, release. |
| **Caveats** | While a template repository is private, anyone generating projects needs read access to it. Rulesets protect `main` and the release tags; "CI must be green before tagging" remains a process rule, because tags are created by the maintainer. |

## GitHub Actions

| | |
|---|---|
| **Problem** | Running every gate that does not need local services or cross-repository checkouts on every push and PR. |
| **Why selected** | Built into GitHub; macOS runners exist for Xcode. |
| **Invoked by** | Push to `main`, pull requests. |
| **Produces** | Job results; downloadable evidence (`junit.xml`, console log, `metadata.txt` with the commit under test, installed packages) for 30 days in the platform and web template. |
| **Phase** | CI. |
| **Caveats** | No secrets are stored and each workflow checks out only its own repository, so cross-repository live checks are local release gates. GitHub's macOS runners do not reliably provide Docker, so the native e2e is local. See [GitHub CI versus local](../testing/ci.md). |

## Claude Code

| | |
|---|---|
| **Problem** | Implementing and verifying changes across several repositories with consistent rules. |
| **Why selected** | Reads `CLAUDE.md` automatically; every repository's `CLAUDE.md` is one line, `@AGENTS.md`, so the same rules serve any agent that reads `AGENTS.md`. |
| **Invoked by** | You, in a repository directory. |
| **Consumes** | `AGENTS.md` (repository rules), `ios/AGENTS.md` (native layer rules), `docs/NEXT_SESSION.md` (handoff), your prompt. |
| **Phase** | Development, release preparation. |
| **Caveats** | The rules forbid committing, pushing, tagging or adding dependencies without explicit approval, and work is not done until the gate passes with actual results reported. Harness permission checks are a second layer, not the only one (see the [destructive-command incident](../ai-workflow/instructions.md#the-destructive-command-incident)). |

## Zensical (this manual)

Static site generator for this wiki (`zensical` 0.0.74, locked in `uv.lock`), Material-style theme, dark `slate` palette by default, Mermaid diagrams rendered in the browser. **Phase:** documentation.
