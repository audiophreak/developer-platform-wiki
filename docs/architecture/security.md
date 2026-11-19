# Security and trust boundaries

**Verified plus recommendations.** The important boundaries are the developer workstation, downloaded template and package registries, generated code, GitHub credentials, CI runners, and eventual deployment systems. The platform never handles Git credentials, disables terminal prompting, redacts credentials from error messages, and makes `doctor` read-only. Both release workflows use `contents: read` and disable persisted checkout credentials.

Treat template files and dependencies as executable supply-chain inputs. Inspect install scripts and generated workflows before running them. Use least-privilege tokens; keep secrets out of prompts, source, issue text, artifacts, and logs. Avoid placing secrets into template answers unless the template explicitly supports secure, non-persistent input. Review workflow permissions and third-party Actions pins in source.

This wiki is local-first and contains no credentials or private source code. Its preview server is intended for localhost use. Keep the proposed repository private and do not configure public hosting. See [security practices](../operations/security.md).
