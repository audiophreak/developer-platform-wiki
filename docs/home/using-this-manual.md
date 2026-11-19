# How to use this manual

## Who it is for

You are technically experienced but new to this platform. The manual assumes you can read Python, TypeScript and Swift, use a terminal and Git, and understand HTTP. It does not assume you know Copier, Better Auth, the Swift OpenAPI Generator, or how the three repositories relate.

## How it is organized

Each section has a different job:

- **Getting Started** is a tutorial. Read it in order once.
- **Command Reference** and **Tools and Components** are reference. Look things up.
- **Architecture**, **Web Application** and **Native iOS** explain design and the reasons behind it.
- **Testing**, **Upgrade and Recovery** and **Troubleshooting** are operational procedures.
- **AI-Assisted Development** describes how work on the platform is actually done.

## Conventions

| Convention | Meaning |
|---|---|
| `devkit ...` | Run from the `developer-platform` checkout as `uv run devkit ...`. The manual shortens it to `devkit` once the context is clear. |
| `PROJECT` | A generated application's directory (the Git repository root). |
| `~/Developer/...` | The conventional sibling layout of the checkouts ([Repositories and setup](../getting-started/setup.md)). Adjust if yours differs. |
| *web layer*, *native layer* | The two Copier templates applied to one project: `web-core-template` owns everything except `ios/`; `native-ios-template` owns only `ios/`. |
| **Release gate** | A check that must pass locally before a release is tagged, because CI cannot run it. |

Callouts are used sparingly:

!!! danger "Danger"
    An action that can lose data or published state. Read the whole callout before acting.

!!! warning "Warning"
    A common way to get stuck, or behaviour that surprises people.

!!! note "Note"
    Background or a precise detail worth knowing.

!!! info "Source"
    Where a fact comes from, when it matters.

## Authority and freshness

The released source is authoritative. When this manual and a repository disagree, the repository at its release tag wins, and the disagreement belongs in the [source verification map](../reference/source-map.md) and should be fixed here. The manual records a few places where the repositories' own documentation is out of date relative to their code; those are listed there too.

The manual describes **only released behaviour** at the baseline tags. Nothing on an unmerged branch is documented as available.

## Browsing it

```bash
cd ~/Developer/developer-platform-wiki
uv sync --locked
uv run zensical serve --open
```

The site opens in dark mode; the header toggle switches to light. Diagrams are rendered in the browser by Mermaid, which the theme loads from `unpkg.com`, so diagrams need network access while browsing. See [Maintaining this manual](../reference/maintenance.md) for building and validating.
