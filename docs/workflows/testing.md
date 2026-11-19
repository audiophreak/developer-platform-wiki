# Test an application

For a generated Web Core v0.1.0 app, run `npm ci` followed by `npm run check`. That gate runs lint, Next.js route type generation plus `tsc --noEmit`, Prettier check, Vitest, and production build. Run the full check before opening a pull request; CI repeats it.

The platform repository uses `uv run --locked pytest`; its CI runs the suite on Python 3.12 and 3.14. A test marked integration can use a real sibling template checkout. These are separate test layers: platform tests validate generation/orchestration, while app tests validate generated application behavior.

A zero exit code is evidence only for the executed checks, not proof of authorization correctness or production readiness. See [validation gates](../architecture/validation-gates.md) and [Vitest](../technology/vitest.md).

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
