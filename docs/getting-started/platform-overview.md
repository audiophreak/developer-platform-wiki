# Developer Platform overview

**Verified against release tags `developer-platform v0.2.0` and `web-core-template v0.1.0` on November 16, 2026.** The repositories are separate, independently versioned projects.

The platform provisions macOS development workstations and generates applications from versioned Copier templates through a small Python CLI named `devkit`. At v0.2.0, `devkit doctor` is a read-only workstation check and `devkit new` generates from the Web Core profile. The platform profile declares the template version range it supports, the required Node.js major, and allowed template options.

The baseline is Developer Platform `v0.2.0` and Web Core Template `v0.1.0`. Version identifiers are Git tags; neither repository currently has GitHub Release objects. The v0.2 platform supports Web Core template `>=0.1.0,<0.2.0`. `full-stack` and `native-ios` are reserved profiles, not implemented. Optional Zod and `devkit upgrade` appear in open draft PRs and are **not released**.

## Conceptual division of responsibility

- **Platform tooling**: `devkit doctor` checks prerequisites; `devkit new` validates safe path inputs and declared option names, resolves a supported template release, then invokes Copier.
- **Template**: an independently versioned Copier source. v0.1.0 provides Next.js 16 / React 19 / strict TypeScript / Tailwind CSS v4 / shadcn/ui, plus ESLint, Prettier, Vitest, and an Actions check workflow.
- **Generated application**: a separate project that records template origin and commit in `.copier-answers.yml`; the app gets its own Git history and evolves independently.

This resembles an infrastructure provisioning pipeline: a platform CLI orchestrates inputs, a template acts like a versioned module, and the generated repository is the provisioned workload. The analogy is useful for ownership and repeatability, but generated source code is not a live instance that automatically inherits every template change.

## What to verify against source

The [first-app tutorial](first-application.md) now follows the released CLI contract. The exact generated file inventory and all option semantics should be rechecked after each template tag. Keep draft PR features in a clearly labeled preview section until merged and released.

See the [architecture overview](../architecture/overview.md), [devkit and Copier](../architecture/devkit-copier.md), and [release and compatibility record](../reference/releases.md).
