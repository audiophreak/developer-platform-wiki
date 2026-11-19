# Release and compatibility information

## Verified baseline

| Component | Version | Evidence |
|---|---|---|
| Developer Platform | `v0.2.0` | Git tag; source reviewed |
| Web Core Template | `v0.1.0` | Git tag; source reviewed |
| Developer Platform source SHA | `11caaef9aaac2340d25426fbd61a17f808aecba5` | `v0.2.0` tree |
| Web Core Template source SHA | `057d60853fbc53b2dad10d59ef54b4a20917048f` | `v0.1.0` tree |
| Compatibility | Platform v0.2.0 supports template `>=0.1.0,<0.2.0` | Profile registry |
| Python | `>=3.12` | Platform `pyproject.toml` |
| Node.js | 26.x (`>=26 <27`) | Template `.nvmrc` and `package.json` |

Versions are Git tags. The GitHub Releases API returned no release objects for either repository; the tags and repository changelogs document release history.

## Draft proposals (not released)

- Developer Platform draft PR #1 proposes v0.3.0, `devkit upgrade`, safety tooling, and contract snapshots.
- Web Core Template draft PR #1 proposes v0.2.0, optional Zod, strict booleans, and an npm lockfile matrix.

Both PRs are marked “Draft: do not merge or tag.” Do not treat proposed changes as current product behavior.

## Updating this page

For each refresh, record both tags and commit SHAs, Python/Node support, template compatibility, and breaking changes. Link behavior claims to source, tests, or workflows. Keep prior versions visible rather than silently rewriting release history.

The detailed [source verification map](source-map.md) lists the files reviewed and their use in this wiki.
