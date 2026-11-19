# Content maintenance workflow

Treat documentation changes like code: work on a focused branch, update Markdown, run local checks, review the diff, and use the private repository's pull-request process.

## Add or change an article

1. Choose a file under the matching `docs/` subject directory and use lowercase hyphenated names.
2. Cover the purpose, problem solved, interactions, operation, failure modes, tradeoffs, and official references that fit the topic.
3. Distinguish **Verified**, **General concept**, **Pending source verification**, and **Planned** claims. For implementation facts, record source tag and review date.
4. Add or rename the path in `nav` inside `zensical.toml`. Sidebar sections are explicit there.
5. Link related pages and add useful cross-links from existing pages.
6. Write Mermaid as a fenced `mermaid` block. Preview the rendered diagram in Chrome.

## Preview and validate

```bash
uv run zensical serve --open
python3 scripts/check_links.py
uv run zensical build --strict
```

Inspect navigation, breadcrumbs, TOC, search, code rendering, Mermaid, dark mode, and mobile layout. A successful build validates site generation but does not guarantee every diagram is legible; inspect changed diagrams visually.

## Refresh implementation details after a platform release

1. Read the platform and template release tags; record tag and commit SHA.
2. Compare changelog, README, source, tests, generated output, and workflows.
3. Separate features in merged/tagged releases from draft PR proposals.
4. Update commands, versions, option tables, support ranges, and compatibility notes with source links.
5. Search for old versions and feature names, run the link checker and strict build, and inspect the rendered pages.

The wiki does not automatically synchronize with application source. A human must re-check the sources at each release.

## Find stale documentation

Search pages labeled Pending source verification, old version strings, removed commands, outdated external links, and planned pages whose source milestone now exists. The future CI freshness check is backlog work, not an implemented feature.
