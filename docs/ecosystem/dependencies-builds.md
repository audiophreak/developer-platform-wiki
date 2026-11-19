# Dependencies and build systems

A dependency is code or tooling that a project consumes. A package manager resolves dependency names and versions into a graph; a lockfile records a concrete resolution. A build system transforms source into output suitable for execution or deployment. These are connected stages, not synonyms.

For this project context, Python tooling is resolved by uv and web application dependencies by npm. Next.js wraps several frontend build tasks. A clean, lockfile-based install lets another machine or CI reproduce the selected graph more reliably than resolving ranges afresh.

When an install fails, distinguish registry/network problems, incompatible runtime versions, invalid version constraints, native compilation problems, and stale lockfiles. Avoid deleting lockfiles as a first fix; see [dependency troubleshooting](../operations/dependencies.md).
