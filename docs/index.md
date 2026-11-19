# Developer Platform Knowledge Base

Welcome to the technical field guide for building applications with the AI-assisted Developer Platform. This wiki connects the tools, workflows, and architecture behind reusable web application development, and gives you a practical path from a new workstation to a tested application.

!!! warning "Implementation verification status"
    The private repositories were inspected at Developer Platform `v0.2.0` and Web Core Template `v0.1.0`. See the [source map](reference/source-map.md) for tags, commit SHAs, and reviewed files. Draft pull requests are labeled separately and are not treated as released functionality.

## Start here

1. Read the [application development ecosystem](ecosystem/overview.md) to orient yourself to the tools and the boundaries between them.
2. Review the [architecture overview](architecture/overview.md), which separates verified design intent from unknown implementation detail.
3. Follow [Create your first application](getting-started/first-application.md) for a safe, inspectable Copier-based tutorial.
4. Use [Working with Claude Code](workflows/claude-workflow.md) and [Git branches and pull requests](workflows/branches-prs.md) as daily workflow references.

## What this wiki covers

The sidebar maps the full intended manual: getting started, ecosystem concepts, technology references, platform architecture, workflows, full-stack and iOS development, operations, learning labs, and reference material. Articles marked **Planned** are navigation anchors for future content rather than completed guides.

## Learning objectives

By using the completed foundation, you should be able to explain how the Python-side provisioning tools differ from the Node-side application toolchain; trace how a template becomes a working project; make a scoped change with Claude Code; and understand what local checks and CI do before a pull request is accepted.

## Status vocabulary

| Label | Meaning |
|---|---|
| **Verified** | Checked against repository source or an authoritative source and dated. |
| **General concept** | Established tool behavior explained without asserting that this platform uses every option. |
| **Pending source verification** | The topic is in scope, but implementation details need comparison with a private source repository or released artifact. |
| **Planned** | The article is a backlog placeholder, not operating guidance. |

## Feedback and maintenance

Keep article source in Git as Markdown. Follow the [content maintenance workflow](reference/maintenance.md) when adding pages or revising claims, and consult the [prioritized backlog](reference/backlog.md) to choose follow-up work. The site is static and locally previewable; it does not synchronize itself with application code.
