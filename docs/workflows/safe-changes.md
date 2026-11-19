# Make changes safely

Begin with `git status --short` and use a focused branch. Read `AGENTS.md` and relevant code before editing. State an observable goal and scope. Inspect the diff for unrelated changes, dependency churn, secrets, and generated files; run the checks documented by the project.

The generated Web Core `AGENTS.md` says to plan nontrivial work first, keep changes focused, avoid dependency changes without approval, never commit/push/merge/deploy without explicit authorization, and require `npm run check` to pass. Its secure-coding rules require server-side validation of untrusted input and authorization near the data. These rules apply to that generated project; platform repository instructions should be read separately.

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
