# aws-data-engineering-shenanigans

AWS CDK playground managed by [projen](https://projen.io) and deployed by
GitHub Actions (push to `main`).

## Layout

- **`.projenrc.py` is the single source of truth.** Edit it, then run
  `npx projen` to re-synthesize every generated file. Generated files are
  read-only and guarded by projen's anti-tamper mechanism.
- `ruff.toml` and `ty.toml` are hand-authored (projen has no components
  for them).
- `constants.py` pins the AWS account and region; the deploy workflow
  exports them for OIDC.

## Local checks (pre-commit)

`.pre-commit-config.yaml` is projen-generated and mirrors the CI checks:

| hook            | runs                                        | when                             |
| --------------- | ------------------------------------------- | -------------------------------- |
| `ruff-lint-fix` | `.venv/bin/ruff check --fix`                | staged `.py` files               |
| `ruff-format`   | `.venv/bin/ruff format`                     | staged `.py` files               |
| `ty-check`      | `.venv/bin/ty check --error-on-warning .`   | staged `.py` triggers whole-repo |

Fixer hooks rewrite files in place; pre-commit then fails the commit
once — re-stage with `git add` and commit again.

The hooks invoke the binaries `uv sync` places in `.venv` (versions come
from `uv.lock`), so they work from any shell or GUI git client, without
touching your shell's PATH.

Hooks are installed by the install task: `npx projen install` after
cloning. Useful invocations:

```console
$ uv run pre-commit run --all-files     # full sweep
$ SKIP=ruff-format git commit -m "..."  # skip one hook for one commit
```
