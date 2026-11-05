# aws-data-engineering-shenanigans

AWS CDK playground managed by [projen](https://projen.io) and deployed by
GitHub Actions (push to `main`).

## Layout

- **`projen_config.py` is the single source of truth.** `.projenrc.py` is
  a thin entry shim over it; shared enums live in `projen_types.py` and
  `projen_setup.py` assembles the project from the config. Edit the
  config, then run `npx projen` to re-synthesize every generated file.
  Generated files are read-only on disk — never hand-edit them.
- **Deployment environments** also live in `projen_config.py`
  (`DEPLOYMENT_ENVIRONMENTS`): one row per environment (a unique AWS
  account ID + region; currently a single `dev` row). `app.py`
  instantiates one stack per row (`aws-data-engineering-shenanigans-<env>`),
  and the build and deploy workflows render the rows into their strategy
  matrices, where they resolve the per-environment OIDC role and region
  (deploy targets stacks via `cdk deploy "*-<env>"`).
- `ruff.toml` and `ty.toml` are projen-managed raw files (projen has no
  dedicated components for them).
- `constants.py` pins the tool versions that `projen_config.py` references.
- The security scanner policy files (`.checkov.yaml`, `trivy.yaml`,
  `.gitleaks.toml`, `uv.toml`, `zizmor.yml`, `.hadolint.yaml`,
  `osv-scanner.toml`) are projen-managed via `projen_config.py`
  (see the Security checks section).

## Local checks (pre-commit)

`.pre-commit-config.yaml` is projen-generated and mirrors the CI checks:

| hook                 | runs                                      | when        |
| -------------------- | ----------------------------------------- | ----------- |
| `ruff-lint-fix`      | `.venv/bin/ruff check --fix`              | staged `.py` files               |
| `ruff-format`        | `.venv/bin/ruff format`                   | staged `.py` files               |
| `ty-check`           | `.venv/bin/ty check --error-on-warning .` | staged `.py` triggers whole-repo |
| `basedpyright-check` | `.venv/bin/basedpyright`                  | staged `.py` triggers whole-repo |

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

## Security checks

Eight scanners run in parallel (as background steps) in the `scan` job of
the `security` workflow on every pull request, and locally via the
`security` task (each scanner has its own `security:<name>` task). All
tool versions are pinned in `projen_config.py`; CI downloads the six
standalone binaries digest-pinned from their GitHub releases, so a
silently repointed release URL cannot swap a binary. The `uv audit` run
goes through the pinned uv itself, which reuses the lockfile.

| scanner              | tool                 | input               | policy file      | local task                     |
| -------------------- | -------------------- | ------------------- | ---------------- | ------------------------------ |
| `secret-scan`        | `gitleaks`           | full git history    | `.gitleaks.toml` | `security:secret-scan`         |
| `sast`               | `opengrep`           | git-tracked sources | (rulesets `p/`)  | `security:sast`                |
| `misconfig-scan`     | `trivy`              | workspace files     | `trivy.yaml`     | `security:misconfig-scan`      |
| `sca-python`         | `uv audit` (preview) | `uv.lock`           | `uv.toml`        | `security:sca-python`          |
| `iac-scan`           | `checkov`            | synthesized CF template (`cdk.out/`) | `.checkov.yaml` | `security:iac-scan` |
| `github-actions-scan` | `zizmor`            | `.github/workflows` | `zizmor.yml`     | `security:github-actions-scan` |
| `sca-multi-language` | `osv-scanner`        | manifests and lockfiles | `osv-scanner.toml` | `security:sca-multi-language` |
| `dockerfile-lint`    | `hadolint`           | Dockerfiles         | `.hadolint.yaml` | `security:dockerfile-lint`     |

All scans fail closed: a finding fails the job. Consciously accepted
findings are silenced in the scanner's policy file (currently empty — none
accepted yet) — always with a written reason next to the entry, and
reviewed quarterly — never by narrowing what a scan looks at. For
opengrep, code-level exceptions use an inline `# nosemgrep: <rule-id>`
comment. For checkov, suppression is attached to the resource via CDK
`add_metadata` (see the Checkov section). To suppress a finding for a
dependency instead, upgrade it first (like `pytest` was when `uv audit`
flagged `PYSEC-2026-1845`); the `[audit].ignore` entries in `uv.toml`
are the last resort, for findings that are demonstrably unreachable.

**cdk-nag (synthesis-time gate).** Configured in `app.py`: cdk-nag v3
(`AwsSolutions` + NIST 800-53 rev 5 packs) runs as CDK policy-validation
plugins inside every `cdk synth`/`diff`/`deploy`. Unsuppressed errors
fail everywhere, warnings fail CI too (the built-in `synth` task is
overridden in `projen_config.py` to `cdk synth --strict`). Intentional
findings are acknowledged on the app scope, not in a policy file:

```python
Validations.of(app).acknowledge(
    Acknowledgment(id="AwsSolutions::AwsSolutions-EC23", reason="..."),
)
```

The empty-stack warning `CloudFormation-Validate::F0001` is
acknowledged in `app.py` until the first real resource lands.

**Checkov (IaC).** Checkov now scans the synthesized CloudFormation
template in `cdk.out/` (step `IaC scan` in the `scan` job). The
`skip-check` mechanism in `.checkov.yaml`/CLI is broken in 3.4.0 (silent
no-op), so it is never used. To suppress a finding, attach it to the
resource in CDK instead:
```
cfn_resource.add_metadata("checkov", {
    "skip": [{"id": "CKV_AWS_27", "comment": "reason"}],
})
```
The sample SQS queue was removed, so CKV_AWS_27 / trivy AWS-0096 no
longer apply. The `IaC scan` step synthesizes `cdk.out/` without AWS
auth (the stack is empty and uses no context lookups); if future CDK
code needs lookups, add `JobStepName.AWS_CREDENTIALS` (declared once in
`GITHUB_JOB_STEPS`) to that job's step list in `projen_config.py`. The scan is
vacuous until resources are added. The full investigation notes live in
PR #5.
Local prerequisites: `gitleaks`, `opengrep`, `trivy`, `zizmor`,
`osv-scanner` and `hadolint` (standalone binaries) plus `checkov` (via
`uvx`) must be on `PATH` to run their tasks (pin the versions used
by CI - see the install steps in
`.github/workflows/security.yml`). The `uv` version used by your
shell only has to satisfy `uv audit`; the `checkov` task also needs the
CDK CLI to synthesize `cdk.out/`.
Manual one-time changes are now minimal; both were applied via the GitHub
API as part of this PR (see the PR description for the exact payloads):

1. **Branch rules on `main`** — pushes to `main` require an open PR whose
   status checks pass (`check`, `build (dev, 925000840053,
   eu-west-1)`, `scan`, `Validate PR title`), and
   force-pushes/deletions of `main` are blocked.
   Recreate in Settings → Rules → Rulesets if the account ever resets, or
   via the API call documented in the PR. The `build` check name embeds
   the environment's matrix row (GitHub joins a leg's row values with
   commas) and one leg is produced per environment — when a new
   environment row is added, append its leg's check name to this ruleset.
2. **Native secret scanning** (complements the gitleaks job with
   near-real-time push prevention): Settings → Code security → enable
   *Secret scanning* and *Push protection* (Settings → Code security &
   analysis; a UI toggle, not part of the automated setup).

