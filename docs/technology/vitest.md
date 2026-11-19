# Vitest and testing tools

Web Core v0.1.0 pins Vitest 5.0.5 and runs it with `npm run test` (`vitest run`) as part of `npm run check`. The template contains page and button tests and a `vitest.config.mts`; it does not define a coverage threshold in the released package scripts. The template itself also has Python render and end-to-end tests, separate from generated-app Vitest tests.

Use unit/component tests for small behavior units and keep production build/type checks as separate gates; none substitutes for integration or browser-level user-flow testing. Coverage policy and a browser e2e suite are not implied by the current v0.1.0 setup.

Reference: [Vitest documentation](https://vitest.dev/guide/).
