# Template architecture and versioning

**Verified against platform v0.2.0 and template v0.1.0.** The two repositories have independent SemVer tag series. The platform profile supports `>=0.1.0,<0.2.0` and currently declares Node major 26 plus the `cache_components` boolean option.

A template release is an input to project generation. Default published mode selects the newest template release inside the devkit-supported range; `--template-ref` selects an explicit release. Generated `.copier-answers.yml` records the source URL and rendered commit/tag. Template v0.1.0 says 0.x minor releases may be breaking, including new Node majors, renamed/removed questions, or defaults that alter generated apps. A generated application then evolves independently through commits.

The platform tests the contract between the profile registry and template `copier.yml`. Breaking template contract changes need a coordinated platform support-range update. See [upgrade lifecycle](upgrade-lifecycle.md) and [release reference](../reference/releases.md).
