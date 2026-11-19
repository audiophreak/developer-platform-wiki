# Start an application

Follow the exact v0.2.0 workflow in [Create your first Web Core application](../getting-started/first-application.md): `uv sync`, read-only `uv run devkit doctor`, review `devkit new ... --dry-run`, generate the app, then `npm ci` and `npm run check`. Keep both checkouts' versions in view; the v0.2 platform supports template releases `>=0.1.0,<0.2.0`.

The command does not create a remote repository or install app dependencies. It also refuses existing output paths. Keep the generated app separate from the platform checkout.

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
