# The AI-assisted workflow

The platform was built, and is meant to be extended, with AI coding agents (Claude Code) doing most of the implementation, under rules written into every repository and verified by tests and gates that do not trust the agent's own report.

## The workflow

```mermaid
flowchart TD
  owner([Owner: goal and constraints]) --> brief[Work package prompt<br/>scope, authorized repos, gates, stop conditions]
  brief --> read[Agent reads AGENTS.md via CLAUDE.md,<br/>docs/NEXT_SESSION.md, current tags]
  read --> plan[Plan; wait for approval<br/>on architecture, dependencies, breaking changes]
  plan --> impl[Implement on a feature branch<br/>small commits; tests with every behaviour change]
  impl --> gates{Local gates<br/>uv run pytest · npm run check ·<br/>test:db · ios test.sh}
  gates -- fail --> impl
  gates -- pass --> report[Report actual results,<br/>including failures and skips]
  report --> review[Independent review<br/>separate session or reviewer;<br/>re-run gates, read the diff]
  review -- findings --> impl
  review -- accepted --> pr[Push branch, PR, CI green<br/>on 3.12 + 3.14 / macOS]
  pr --> approve{Owner approves<br/>merge and tag?}
  approve -- no --> impl
  approve -- yes --> tag[Merge commit → annotated tag<br/>template first, platform last]
  tag --> accept[Published-pair acceptance<br/>fail-closed audit]
  accept -- fail --> fix[Fix forward: patch release] --> impl
  accept -- pass --> handoff[Update NEXT_SESSION.md,<br/>CHANGELOGs, docs]
```

## Principles, as practised

| Principle | How it is enforced |
|---|---|
| Rules live in the repository, not in the prompt | `AGENTS.md` in every repo and every generated project; `CLAUDE.md` is one line, `@AGENTS.md` |
| The agent does not decide architecture | "Plan first … wait for approval on architectural decisions"; `devkit` itself refuses to pick a database provider |
| The agent does not publish | "Do not commit, push, tag, publish, deploy or rewrite history unless explicitly asked. Never move or delete a published tag." |
| The agent does not add dependencies | "Do not add, upgrade or remove dependencies without approval"; exact pins; two-week age rule enforced by `exclude-newer` and tests |
| Done means the gate passed | "Work is not done until `uv run pytest` / `npm run check` passes. Report actual results, including failures." |
| Destructive commands are impossible to slip in | a test in each repo fails if code, CI or documented snippets contain them |
| Trust nothing the agent says about itself | independent review and a fail-closed acceptance audit that parses exit codes and counts |
| Authorized repositories only | each work package names the repositories that may change; acceptance gates prove the others did not |

## Pages

- [AGENTS.md, CLAUDE.md and trust boundaries](instructions.md)
- [Sessions, prompts and review](sessions.md)
