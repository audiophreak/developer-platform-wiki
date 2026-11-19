# Build and link validation report

**Validated:** November 16, 2026 (client date)  
**Tool:** Zensical `0.0.74` from `uv.lock`  
**Scope:** the local wiki source and generated static site

| Check | Result |
|---|---|
| `uv sync --locked` | Passed; environment resolved from committed lockfile |
| `uv run zensical build --clean --strict` | Passed; Zensical reported no issues |
| Explicit navigation target check | 75 sidebar entries resolve |
| Local Markdown link check | Passed; no missing local targets |
| Mermaid source blocks | 7 fenced blocks found |
| Mermaid build containers | 7 corresponding `.mermaid` containers in generated HTML |
| Generated HTML pages | 75 `index.html` pages |
| Local preview smoke check | `/`, `/ecosystem/overview/`, and `/architecture/devkit-copier/` returned HTTP 200 from `zensical serve` |
| Initial color scheme | Dark (`slate`); header toggle switches to light (`default`) |

The Mermaid check verifies that Zensical builds each fenced block into its Mermaid integration container. A human should still inspect diagrams in Chrome after changing them for layout and legibility. No automated browser screenshot or production deployment was performed.
