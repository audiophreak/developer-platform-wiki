# Claude Code and AI-assisted development

Claude Code is an agentic coding tool that can inspect a repository, edit files, and run commands with the permissions of its environment. It is useful for accelerating bounded tasks, but its output remains a proposed code change that needs human review and normal validation.

## A controlled working loop

1. Establish the current branch, working tree, project instructions, and relevant tests.
2. State a concrete outcome, scope, constraints, and acceptance checks.
3. Ask the agent to inspect before editing when repository structure or behavior is unclear.
4. Review the plan and diff; reject unrelated changes and unrequested dependency or configuration drift.
5. Run the relevant tests, type checks, lint, and build yourself or inspect their actual output.
6. Commit through a focused branch and pull request.

This resembles delegated operations automation: least privilege, narrow blast radius, change review, and an auditable execution record. Keep secrets out of prompts and logs. Do not let an agent bypass repository security controls or run destructive commands without explicit authorization.

Project-level instruction files such as `CLAUDE.md` can document repository conventions. Their actual content and tool-specific permissions should be reviewed rather than assumed. Authoritative resource: [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/overview). See also [safe changes](../workflows/safe-changes.md).
