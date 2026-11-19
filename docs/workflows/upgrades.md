# Upgrade generated applications

**Released path (template v0.1.0):** use Copier directly; no `devkit upgrade` command is released. Read the template changelog and select an explicit compatible tag. Ensure the app working tree is clean and `.copier-answers.yml` is committed. Confirm Git can authenticate to the private template.

```bash
copier update --vcs-ref v0.1.1 --defaults --skip-answered
```

Replace `v0.1.1` with the chosen tag; this example tag is illustrative, not a claim that it exists. Review the full diff and search for `<<<<<<<`, `=======`, and `>>>>>>>` conflict markers. Resolve `package.json` first, then run `npm install` to regenerate the lockfile, followed by `npm run check`. Commit the resolved upgrade as one reviewable change.

Never omit `--vcs-ref`: Copier otherwise selects the newest tag, potentially a breaking 0.x minor release. For a question added after generation, Copier applies its default unless overridden with `--data`.

**Draft proposal:** platform PR #1 proposes `devkit upgrade`, but it is not released. See [upgrade lifecycle](../architecture/upgrade-lifecycle.md).

Related topics will be linked here as the manual expands. See the [documentation backlog](../reference/backlog.md) for priority and completion evidence.
