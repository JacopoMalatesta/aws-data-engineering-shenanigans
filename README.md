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
- The security scanner policy files (`.checkov.yaml`, `trivy.yaml`,
  `.gitleaks.toml`, `uv.toml`) are projen-generated via `.projenrc.py`
  (see the Security checks section).

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

## Security checks

Five scanners run in parallel on every pull request (the `security-checks`
workflow, one job each) and locally via the `security` task (each scanner
has its own `security:<name>` task). All tool versions are pinned in
`.projenrc.py`; CI downloads the three standalone binaries digest-pinned
from their GitHub releases, so a silently repointed release URL cannot
swap a binary. The `uv audit` run goes through the pinned uv itself,
which reuses the lockfile.

| job              | scanner              | input               | policy file      | local task                 |
| ---------------- | -------------------- | ------------------- | ---------------- | -------------------------- |
| `sca`            | `uv audit` (preview) | `uv.lock`           | `uv.toml`        | `security:sca`             |
| `sast`           | `opengrep`           | git-tracked sources | `(rulesets p/)`  | `security:sast`            |
| `secret-scan`    | `gitleaks`           | full git history    | `.gitleaks.toml` | `security:secret-scan`     |
| `misconfig-scan` | `trivy`              | workspace files     | `trivy.yaml`     | `security:misconfig-scan`  |
| `iac-scan`       | `checkov`            | synthesized CF template (`cdk.out/`) | `.checkov.yaml` | `security:iac-scan` |

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

**Checkov (IaC).** Checkov now scans the synthesized CloudFormation
template in `cdk.out/` (job `checkov`). The `skip-check` mechanism in
`.checkov.yaml`/CLI is broken in 3.4.0 (silent no-op), so it is never
used. To suppress a finding, attach it to the resource in CDK instead:
```
cfn_resource.add_metadata("checkov", {
    "skip": [{"id": "CKV_AWS_27", "comment": "reason"}],
})
```
The sample SQS queue was removed, so CKV_AWS_27 / trivy AWS-0096 no
longer apply. The `iac-scan` job synthesizes `cdk.out/` without AWS
auth (the stack is empty and uses no context lookups); if future CDK
code needs lookups, add `AWS_AUTH_STEPS` to that job. The scan is
vacuous until resources are added. The full investigation notes live in
PR #5.
Local prerequisites: `gitleaks`, `opengrep`, `trivy` and `checkov`
(via `uvx`) must be on `PATH` to run their tasks (pin the versions used
by CI - see the install steps in
`.github/workflows/security-checks.yml`). The `uv` version used by your
shell only has to satisfy `uv audit`; the `checkov` task also needs the
CDK CLI to synthesize `cdk.out/`.
Manual one-time changes are now minimal; both were applied via the GitHub
API as part of this PR (see the PR description for the exact payloads):

1. **Branch rules on `main`** — pushed to `main` requires an open PR whose
   status checks pass (`build`, `Validate PR title`, `sca`, `sast`,
   `secret-scan`, `misconfig-scan`, `iac-scan`), and force-pushes/deletions
   of `main` are blocked.
   Recreate in Settings → Rules → Rulesets if the account ever resets, or
   via the API call documented in the PR. The check names are matched by
   job id; keep CI job ids in sync with (or update) the ruleset.
2. **Native secret scanning** (complements the gitleaks job with
   near-real-time push prevention): Settings → Code security → enable
   *Secret scanning* and *Push protection* (Settings → Code security &
   analysis; a UI toggle, not part of the automated setup).

