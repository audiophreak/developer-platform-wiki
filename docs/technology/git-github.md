# Git and GitHub

Git is distributed version control: a commit records a snapshot and its parentage, while a branch is a movable name for a line of development. GitHub hosts Git repositories and layers on access control, issues, pull requests, reviews, and automation.

Use a branch to isolate a focused change. Commit coherent steps with messages that explain intent. Push the branch and open a pull request so reviewers can examine the diff and CI results before merge. A pull request is a review and integration conversation; it is not a separate Git object.

```bash
git status --short
git switch -c docs/clarify-bootstrap
# edit files
git diff --check
git diff
git add docs/
git commit -m "docs: clarify bootstrap workflow"
git push -u origin docs/clarify-bootstrap
```

Always inspect staged changes before committing. Keep credentials out of Git history; removing a secret in a later commit does not make the exposed value safe. The two platform repositories configure Actions for pull requests and main-branch pushes with `contents: read`, but branch protection itself is not configured by these workflow files. References: [Git documentation](https://git-scm.com/doc), [GitHub pull requests](https://docs.github.com/en/pull-requests), [GitHub Actions](https://docs.github.com/en/actions).
