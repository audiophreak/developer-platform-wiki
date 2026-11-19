# Development workstation

**General setup guidance; verify platform-specific minimum versions before use.** The wiki itself needs Python 3.11 or newer, `uv`, Git, and Chrome. Application work additionally uses Node.js and npm. Avoid installing project tools globally when a repository lockfile can pin them.

## Bootstrap this wiki on macOS

After extracting the archive to `~/Developer/developer-platform-wiki`:

```bash
cd ~/Developer/developer-platform-wiki
uv sync --locked
uv run zensical serve --open
```

Open `http://localhost:8000` in Chrome if it does not open automatically. Stop the preview with `Ctrl+C`. Zensical’s embedded server is for local preview, not a production web server.

## Application workstation boundaries

Use `uv` to manage Python tooling for the platform and documentation. Use a Node version compatible with the generated app, then `npm ci` when a committed `package-lock.json` is present. The exact supported Python and Node versions should be taken from the platform's tagged source, not guessed; see [Python and uv versus Node.js and npm](../ecosystem/runtimes-packages.md).

## Basic checks

```bash
git --version
python3 --version
uv --version
node --version
npm --version
```

Record versions when troubleshooting. See [environment diagnostics](../operations/diagnostics.md).
