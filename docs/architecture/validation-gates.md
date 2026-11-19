# Testing and validation gates

**Verified against the release tags.** The Web Core template's `npm run check` runs `lint`, `typecheck`, `format:check`, `test`, and `build` in that order and stops on failure. CI runs `npm ci` then `npm run check`.

A useful gate sequence distinguishes lint, static type checks, formatting, tests, and production build. They catch different classes of defect. Platform CI tests on Python 3.12 and 3.14. The template's test suite includes component/page Vitest tests; the template repository itself separately runs Python tests that render and validate generated projects. Local checks give fast feedback; CI repeats configured checks against the submitted commit.

See [testing workflow](../workflows/testing.md) and [Vitest reference](../technology/vitest.md). Do not claim a gate exists until its source configuration is verified.
