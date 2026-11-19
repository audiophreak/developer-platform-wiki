# Zod and input validation

**Draft PR only; not released as of November 16, 2026.** Web Core template PR #1 proposes an optional Zod 4.6.7 feature, default off, with exact pins, shared schemas under `src/lib/schemas/`, and tests. It also proposes a lockfile matrix so generation does not resolve packages. Until that PR is merged and released, v0.1.0 applications do not include this optional feature.

The educational concept remains relevant: TypeScript catches many type mismatches during development, but data arriving at runtime from forms, APIs, or storage must be validated at the boundary. Zod can express runtime schemas and infer corresponding TypeScript types. Future content should document the released schema locations and trust boundaries after verifying the merged template.

Do not assume Zod is installed or that validation occurs at API boundaries until confirmed in a release. Reference: [Zod documentation](https://zod.dev/).
