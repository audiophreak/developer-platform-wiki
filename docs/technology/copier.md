# Copier

**General concept.** Copier is a tool for generating and updating projects from templates. A template can ask questions, render files, and record metadata that helps relate a generated project to its source template. This makes Copier useful when teams need repeatable project scaffolding with choices.

The Web Core Template v0.1.0 uses Copier 9.19.1. Its `copier.yml` defines prompts, answer validation, the `template/` subdirectory, and `.copier-answers.yml` provenance. It deliberately contains no Copier `_tasks`, `_migrations`, or Jinja extensions, avoiding execution of template hooks during generation. Copier validation is centralized in the template so both direct Copier use and the `devkit` wrapper enforce the same content rules.

Copier updates a generated project by a three-way merge between the original template version, the target version, and the current app files. The template's update guide requires a clean Git tree and explicit target `--vcs-ref`; review inline conflict markers before committing. This is similar to applying a versioned infrastructure module, except the result is source code that app teams own and can modify.

Alternatives include Cookiecutter and custom generators. Copier's update/merge workflow is a central choice here; tradeoff is that generated projects inherit ongoing merge work and need the private template repository's Git access. References: [Copier documentation](https://copier.readthedocs.io/en/stable/), [platform architecture overview](../architecture/overview.md).
