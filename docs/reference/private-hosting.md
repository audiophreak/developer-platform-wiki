# Private hosting options

**Current choice: local preview only.** The wiki has no deployment workflow, cloud resources, or public hosting configuration. This page records options for a later access decision; it does not select or provision a host.

| Option | Access model | Main tradeoff |
|---|---|---|
| Local Zensical preview | `localhost` on the author's workstation | Simplest and currently implemented; readers need the project archive or repository checkout and local tooling. |
| Existing private static web server | Place the generated static files behind an internal network, VPN, or SSO-controlled reverse proxy | Keeps access within an already managed environment; requires server operations and access lifecycle ownership. |
| GitHub Pages private publishing | Repository-member access for an organization-owned project site | GitHub documentation currently requires GitHub Enterprise Cloud for privately published Pages; a private repository alone does not make the Pages site private. Check plan and org policy before considering it. |
| Cloudflare Pages with Access | Identity-gated access policy on the site hostname | Adds an external service and identity/access policy dependencies; verify both Pages and custom-domain policies to avoid an accidentally unprotected hostname. |

For any hosted option, review the intended audience, authentication source, URL exposure, logs/analytics, cache behavior, deletion/retention, and who can deploy. Keep the docs repository private regardless of hosting choice. Do not deploy until access controls are explicitly reviewed.

## Official references

- [GitHub: privately published Pages sites](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/about-privately-published-github-pages-sites)
- [GitHub: creating a Pages site and plan requirements](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Cloudflare: Pages access protection notes](https://developers.cloudflare.com/pages/platform/known-issues/)
- [Cloudflare: Access for Workers and Pages](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)

Checked November 16, 2026. Re-verify vendor plan, access, and pricing before selecting an option.
