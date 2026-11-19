# Update dependencies

Update one ecosystem at a time. For the platform's Python graph, change declared exact pins with uv and commit the matching `uv.lock`. For a generated app, update `package.json` and regenerate `package-lock.json` using the intended npm command. The template maintainer's guide says to use exact npm versions and to choose releases at least two weeks old.

After an app update, run `npm ci` from a clean checkout, then `npm run check`. Review major-version notes and transitive/native changes. Never hand-edit or discard a lockfile as a first troubleshooting step. The optional feature lockfile matrix is draft PR work, not released behavior.

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
