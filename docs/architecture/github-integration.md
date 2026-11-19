# GitHub integration

**Verified against both v0.2.0/v0.1.0 workflows and docs.** `devkit` itself does not create a GitHub repository or manage credentials. For private template reads, Git must authenticate non-interactively; the platform documentation recommends `gh auth setup-git`, which configures GitHub CLI as a Git credential helper. The CLI runs with terminal prompts disabled, never reads or stores the token, and redacts credential-bearing URLs from errors.

The platform CI runs tests on pushes to main and PRs with `contents: read`, Python 3.12/3.14, `uv sync --locked`, and pytest. Generated-app CI runs `npm ci` and `npm run check` on main pushes and PRs, also with read-only contents permission and pinned Actions. The generated app does not need access to the template during normal CI; only generation or `copier update` needs access.

No GitHub repository creation, deployment, or public hosting is part of these released workflows. See [Git and GitHub](../technology/git-github.md) and [private-template access troubleshooting](../operations/install.md).

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
