# Architecture decision records

## ADR-0001: Use Zensical for the local-first wiki

- **Status:** Accepted for bootstrap
- **Date:** 2026-11-16
- **Decision:** Use Zensical, Markdown source, Python/uv tooling, Mermaid, client-side search, and a static build.
- **Context:** The manual needs a navigable local wiki with search, diagrams, low operational overhead, and no cloud account.
- **Reasons:** Official Zensical documentation describes local live preview (`zensical serve`), static build (`zensical build`), integrated Mermaid fences, built-in search, breadcrumbs, TOC, expandable navigation, and theme palettes for light/dark mode.
- **Tradeoffs:** Zensical is evolving; lock its version and check upgrade notes. The embedded server is preview-only. Search is client-side and English UI only at present. Hosting, if ever selected, needs a separate private-access review.
- **Alternatives:** MkDocs Material has an established ecosystem; Docusaurus brings a JavaScript-oriented stack; Sphinx is strong for Python API docs but exceeds this wiki's needs.
- **Consequences:** Keep sources in Git as Markdown, run strict builds and link checks, and do not assume source-code synchronization.

Official references: [installation](https://zensical.org/docs/get-started/), [diagrams](https://zensical.org/docs/authoring/diagrams/), [navigation](https://zensical.org/docs/setup/navigation/), [search](https://zensical.org/docs/setup/search/), [preview](https://zensical.org/docs/usage/preview/), [build](https://zensical.org/docs/usage/build/).
