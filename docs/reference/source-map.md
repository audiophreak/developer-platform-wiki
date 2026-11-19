# Implementation source verification map

Reviewed November 16, 2026 through authenticated access to these private repositories. Links require GitHub access. The content below summarizes release behavior; draft pull requests are separately labeled and never treated as released.

## Release revisions

| Repository | Tag | Commit |
|---|---|---|
| [developer-platform](https://github.com/audiophreak/developer-platform/tree/v0.2.0) | `v0.2.0` | `11caaef9aaac2340d25426fbd61a17f808aecba5` |
| [web-core-template](https://github.com/audiophreak/web-core-template/tree/v0.1.0) | `v0.1.0` | `057d60853fbc53b2dad10d59ef54b4a20917048f` |

## Files reviewed

| Area | Source files | Wiki coverage |
|---|---|---|
| Platform contract | `README.md`, `docs/architecture.md`, `docs/usage.md`, `src/devkit/profiles.py`, `src/devkit/sources.py` | [Platform overview](../getting-started/platform-overview.md), [template versioning](../architecture/template-versioning.md) |
| CLI behavior | `src/devkit/cli.py`, `src/devkit/generate.py`, `src/devkit/validation.py`, `src/devkit/doctor.py` | [devkit and Copier](../architecture/devkit-copier.md), [first app](../getting-started/first-application.md) |
| Private access and publishing | `docs/publishing.md`, `src/devkit/gitutil.py`, `src/devkit/sources.py` | [GitHub integration](../architecture/github-integration.md), [security](../architecture/security.md), [installation troubleshooting](../operations/install.md) |
| CI and versions | both `pyproject.toml` files, both `.github/workflows/ci.yml`, both changelogs | [GitHub Actions](../technology/github-actions.md), [release reference](releases.md) |
| Template questions and validation | `copier.yml`, `docs/maintaining.md` | [Copier](../technology/copier.md), [feature composition](../architecture/feature-composition.md) |
| Generated application | `template/package.json.jinja`, `template/README.md.jinja`, `template/AGENTS.md`, template directory tree | [generated application](../architecture/generated-app.md), technology references |
| Upgrade behavior | `docs/upgrading.md`, `docs/provenance.md`, `tests/test_upgrade.py` | [upgrade lifecycle](../architecture/upgrade-lifecycle.md), [upgrade workflow](../workflows/upgrades.md) |

## Draft work reviewed

- [Developer Platform PR #1](https://github.com/audiophreak/developer-platform/pull/1) is open and draft, proposing a v0.3.0 milestone with `devkit upgrade`, safety tooling, and contract snapshots. Its body says “do not merge or tag.”
- [Web Core Template PR #1](https://github.com/audiophreak/web-core-template/pull/1) is open and draft, proposing v0.2.0 with optional Zod, strict booleans, and an npm lockfile matrix. Its body says “do not merge or tag.”

Recheck these states before a future documentation release. No release behavior is inferred from the draft branch contents.
