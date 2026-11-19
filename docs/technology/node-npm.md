# Node.js and npm

**General concept.** Node.js is a JavaScript runtime. npm is the default package manager and command runner distributed with Node.js. A Next.js project typically uses Node to run its development server, tests, and production build, while npm resolves packages declared by the project.

The `package.json` records dependency declarations and scripts; `package-lock.json` records a concrete dependency resolution. Use `npm ci` in a clean checkout when the project has a committed npm lockfile. Use `npm run <script>` for scripts defined in `package.json` rather than assuming global binaries.

The v0.1.0 template pins Node major 26 in `.nvmrc` and `package.json` (`>=26 <27`). It uses exact dependency pins and a committed `package-lock.json`; `npm ci` is the clean install used by template CI. `npm run check` runs lint, generated Next.js route type generation plus TypeScript checking, Prettier check, Vitest, and production build.

Keep Node version expectations aligned with `.nvmrc` and CI. Errors may come from an unsupported Node version, an inconsistent lockfile, registry access, or a package's native build step. Inspect the first actionable error rather than deleting lockfiles.

Alternatives include pnpm and Yarn, each with distinct lockfile and workspace behavior. Do not switch package managers without changing CI and documenting the migration. References: [Node.js](https://nodejs.org/en/docs), [npm](https://docs.npmjs.com/).
