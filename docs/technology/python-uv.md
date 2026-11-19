# Python and uv

**General concept.** Python is both a programming language and a runtime. `uv` is a fast Python package and project manager that can resolve dependencies, maintain a lockfile, create a project environment, and run commands inside it.

## Why it matters here

The released platform requires Python `>=3.12`, pins Copier 9.19.1, and exposes the `devkit` command. The platform and template developer environments use uv and `uv.lock`; Python dependencies are project-local, not globally installed. CI runs tests on Python 3.12 and 3.14.

## Operate and troubleshoot

In the platform checkout, `uv sync` creates `.venv` from the exact lock; `uv run devkit doctor` and `uv run devkit new ...` execute within that environment. CI uses `uv sync --locked` to enforce the committed lock. Check `python --version`, `uv --version`, and the active project directory when diagnosing interpreter mismatches. The `doctor` command also checks Python, Git, Copier, Node/npm, uv, `gh` login, and optional tools; it does not install or configure them.

Common issues include an unsupported interpreter, stale lock metadata, an environment created with a different Python, and a shell invoking a global command instead of the project environment. See [runtimes and package managers](../ecosystem/runtimes-packages.md).

## Alternatives and references

Alternatives include the standard library `venv` plus `pip`, Poetry, and Conda. Selection depends on environment and packaging needs; this wiki uses uv for reproducible project-local docs tooling. Authoritative sources: [uv documentation](https://docs.astral.sh/uv/) and [Python documentation](https://docs.python.org/3/).
