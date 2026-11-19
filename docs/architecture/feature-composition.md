# Feature composition

**Current release:** Web Core v0.1.0 exposes one option, `cache_components`, a boolean defaulting to true. It maps to the paired Next.js `cacheComponents` and `partialPrefetching` flags. The platform profile declares the option name/type and sends it through `devkit new --set cache_components=false`; content validation remains in template `copier.yml`.

**Draft proposal:** template PR #1 proposes a general optional-feature registry and makes Zod an opt-in feature. It proposes strict boolean answers and one lockfile per distinct npm dependency set. That design is not part of v0.1.0. Its draft platform companion proposes declaring when options became available and refusing options unsupported by the chosen template release.

The boundary matters: the CLI owns which options are exposed by a profile, while the template owns generated application content and its validation. The template should not need platform-specific logic. See the [devkit/Copier architecture](devkit-copier.md) and [Zod status](../technology/zod.md).

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
