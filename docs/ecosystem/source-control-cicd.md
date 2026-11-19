# Source control, CI/CD, and deployment

Git records project history as commits and branches. GitHub hosts repositories and adds collaboration workflows such as pull requests, review, permissions, and Actions. CI (continuous integration) runs automated checks against changes. CD can automate delivery after specified gates; having CI does not imply that deployment is configured.

Both released repositories run read-only CI on PRs and pushes to `main`. The platform tests Python 3.12 and 3.14; generated apps use the Node version in `.nvmrc`, `npm ci`, and `npm run check`. This is CI validation, not application deployment: no deployment workflow is present in the released template. The diagram in [development lifecycle](../workflows/branches-prs.md) links the stages.
