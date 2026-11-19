# Python and uv versus Node.js and npm

These tools serve two separate toolchains in the platform. Python is used for the platform-side `devkit` by project context; Node.js executes the generated Next.js application and its frontend tooling. `uv` manages Python projects and packages; `npm` manages JavaScript packages. Installing one does not satisfy the other's runtime requirements.

| Tool | Ecosystem | Typical responsibility here |
|---|---|---|
| Python | Python runtime | Execute platform tools and scripts |
| uv | Python project/package manager | Resolve Python dependencies, create environments, run tools |
| Node.js | JavaScript runtime | Run Next.js, tests, linters, and build tooling |
| npm | JavaScript package manager and scripts runner | Resolve packages from `package.json` and lockfile |

The analogy is two isolated control planes on one workstation: both may participate in an app creation workflow, but each has its own package graph, lockfile, and version constraints. A Python virtual environment does not contain npm dependencies; `node_modules` does not provide the Python CLI.

Use the lockfile as the reproducibility boundary: `uv.lock` for uv-managed Python dependencies and `package-lock.json` for npm. In a clean checkout, prefer `uv sync --locked` or `npm ci`, respectively. The released platform requires Python >=3.12; generated apps require Node 26.x. See [Python and uv](../technology/python-uv.md), [Node.js and npm](../technology/node-npm.md), and [dependency failures](../operations/dependencies.md).
