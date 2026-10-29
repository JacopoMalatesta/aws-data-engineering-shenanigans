"""Projen project definition - the single source of truth for this repo.

Edit this file, then re-run it (``npx projen``) to regenerate every
projen-managed file. Never hand-edit those; they are read-only.
"""

from typing import Final

from projen import Task, TomlFile, YamlFile
from projen.awscdk import AwsCdkPythonApp
from projen.github import GitHubOptions, PullRequestLintOptions, SemanticTitleOptions
from projen.github.workflows import Job, JobPermission, JobStep
from projen.vscode import VsCode

PYTHON_VERSION: Final = "3.13"
PROJEN_RUN: Final = "npx projen@0.104.17"
EXPORT_CONSTANTS: Final = """echo "AWS_ACCOUNT_ID=$(uv run python -c 'from constants import AWS_ACCOUNT_ID; print(AWS_ACCOUNT_ID)')" >> "$GITHUB_ENV"
echo "AWS_REGION=$(uv run python -c 'from constants import AWS_REGION; print(AWS_REGION)')" >> "$GITHUB_ENV"
"""

# Security scanner pins (versions + SHA256 of downloaded release assets,
# so a swapped asset fails the download instead of running different code).
GITLEAKS_VERSION: Final = "8.30.1"
GITLEAKS_LINUX_X64_TARBALL_SHA256: Final = (
    "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
)
TRIVY_VERSION: Final = "0.76.1"
TRIVY_LINUX_64BIT_TARBALL_SHA256: Final = (
    "c7cbe3137fb8a48a17574bede3dd6beb16742d1e9772929940fc90082c39d9c0"
)
OPENGREP_VERSION: Final = "1.33.0"
OPENGREP_MANYLINUX_X86_SHA256: Final = (
    "2545812755572e1355ea60f96288f82a26eebed7fc8b512430d49d5667214c24"
)
CHECKOV_VERSION: Final = "3.4.0"

CHECKOUT_V4_PIN: Final = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
SETUP_UV_V5_PIN: Final = "astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86"
SETUP_NODE_V4_PIN: Final = "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020"
AWS_CREDENTIALS_V4_PIN: Final = (
    "aws-actions/configure-aws-credentials@7474bc4690e29a8392af63c5b98e7449536d5c3a"
)

project = AwsCdkPythonApp(
    author_email="jacopomalatesta95@gmail.com",
    author_name="JacopoMalatesta",
    cdk_version="2.275.0",
    # Exact pins: ty is pre-1.0 (unstable API), ruff's rule set evolves,
    # and the pre-commit hooks below must resolve to the same versions
    # CI uses, so all three are pinned rather than ranged.
    dev_deps=["pre-commit@4.6.2", "ruff@0.17.2", "ty@0.0.92"],
    module_name="aws_data_engineering_shenanigans",
    name="aws-data-engineering-shenanigans",
    pytest_options={"version": "9.0.3"},
    uv=True,
    # Pin the venv to CPython 3.13 (uv fetches it automatically) and pin
    # requires-python in pyproject.toml accordingly.
    uv_options={
        "python_exec": PYTHON_VERSION,
        "project": {
            "name": "aws-data-engineering-shenanigans",
            "requires_python": ">=3.13,<4.0",
        },
    },
    version="0.1.0",
    github_options=GitHubOptions(
        pull_request_lint_options=PullRequestLintOptions(
            semantic_title_options=SemanticTitleOptions(
                types=[
                    "build",
                    "chore",
                    "ci",
                    "docs",
                    "feat",
                    "fix",
                    "perf",
                    "refactor",
                    "style",
                    "test",
                ],
            ),
        ),
    ),
)

# Local OpenCode helper scripts are not part of the repo.
project.add_git_ignore(".opencode/")
project.add_git_ignore("*.swp")

# ------------------------------------------------------------------
# Linting, formatting and type checking (ruff + ty).
# Tool configuration lives in ruff.toml and ty.toml at the repo root.
# ------------------------------------------------------------------
lint = project.add_task(
    "lint",
    description="Lint with ruff",
    exec="ruff check .",
)
project.add_task(
    "lint:fix",
    description="Autofix ruff violations (safe fixes only)",
    exec="ruff check --fix .",
)
project.add_task(
    "format",
    description="Format code with ruff",
    exec="ruff format .",
)
format_check = project.add_task(
    "format:check",
    description="Verify ruff formatting",
    exec="ruff format --check .",
)
typecheck = project.add_task(
    "typecheck",
    description="Type check with ty",
    exec="ty check --error-on-warning .",
)

check = project.add_task(
    "check",
    description="Run all static checks: lint, format check, type check",
)
check.spawn(lint)
check.spawn(format_check)
check.spawn(typecheck)

# ------------------------------------------------------------------
# Local git hooks (pre-commit). The config file is projen-generated and
# mirrors the CI checks:
#   - ruff lint+autofix and ruff format run on the staged .py files
#     (fix, then fail once: pre-commit blocks that first commit, and the
#     fixers leave their edits in the working tree to be re-staged);
#   - ty analyses the whole repository (whole-program analysis, so it
#     cannot be scoped to staged files) and runs only when a .py file
#     is staged.
# Hooks invoke the ruff/ty binaries that `uv sync` materializes in
# .venv from uv.lock (still the single source of truth for tool
# versions). Repo-relative entry paths keep them independent of the
# shell's PATH: pre-commit resolves entries containing `/` against the
# repo root. `language: unsupported` (pre-commit >= 4.4, formerly
# `system`) means pre-commit installs no isolated environment.
# ------------------------------------------------------------------
YamlFile(
    project,
    ".pre-commit-config.yaml",
    obj={
        "repos": [
            {
                "repo": "local",
                "hooks": [
                    {
                        "id": "ruff-lint-fix",
                        "name": "ruff check --fix",
                        "entry": "./.venv/bin/ruff",
                        "args": ["check", "--fix"],
                        "language": "unsupported",
                        "types_or": ["python", "pyi"],
                    },
                    {
                        "id": "ruff-format",
                        "name": "ruff format",
                        "entry": "./.venv/bin/ruff",
                        "args": ["format"],
                        "language": "unsupported",
                        "types_or": ["python", "pyi"],
                    },
                    {
                        "id": "ty-check",
                        "name": "ty check",
                        "entry": "./.venv/bin/ty",
                        "args": ["check", "--error-on-warning", "."],
                        "language": "unsupported",
                        "pass_filenames": False,
                        "files": r"\.py$",
                    },
                ],
            },
        ],
    },
)

# Install the git hooks as part of dependency setup: a fresh clone only
# needs `npx projen install` (uv sync provides the pre-commit binary,
# and this step writes .git/hooks/pre-commit).


def _get_task_by_name(name: str) -> Task:
    """Fetch a projen task by name.

    Args:
        name: Registered name of the task (e.g. ``"synth"``).

    Returns:
        The requested task.

    Raises:
        RuntimeError: If no task is registered under that name.
    """
    task = project.tasks.try_find(name)
    if task is None:
        msg = f"no task named {name!r} on the project"
        raise RuntimeError(msg)
    return task


install_task = _get_task_by_name("install")
install_task.exec("pre-commit install")

YamlFile(
    project,
    "trivy.yaml",
    obj={
        "severity": ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "scan": {
            "scanners": ["misconfig"],
            "skip-dirs": [".venv", "cdk.out", "node_modules", ".git"],
        },
    },
)
TomlFile(
    project,
    ".gitleaks.toml",
    obj={
        "title": "aws-data-engineering-shenanigans gitleaks policy",
        "extend": {"useDefault": True},
    },
)
TomlFile(
    project,
    "uv.toml",
    obj={"audit": {"ignore": []}},
)
YamlFile(
    project,
    ".checkov.yaml",
    obj={"framework": ["cloudformation"], "directory": "cdk.out"},
)

security_sca = project.add_task(
    "security:sca",
    description="Audit uv.lock for known vulnerabilities and deprecated projects",
    exec="uv audit --preview-features audit-command",
)
security_sast = project.add_task(
    "security:sast",
    description="Static pattern scan of tracked sources (three rulesets)",
    exec=(
        "opengrep scan --config p/security-audit --config p/owasp-top-ten"
        " --config p/python ."
    ),
)
security_secret_scan = project.add_task(
    "security:secret-scan",
    description="Scan the full git history for leaked credentials",
    exec="gitleaks detect --no-banner --config .gitleaks.toml",
)
security_misconfig_scan = project.add_task(
    "security:misconfig-scan",
    description="Misconfiguration scan of the workspace (Dockerfile etc.)",
    exec="trivy fs --config trivy.yaml --exit-code 1 .",
)
security_iac_scan = project.add_task(
    "security:iac-scan",
    description="IaC policy scan of the synthesized CloudFormation template (cdk.out)",
    exec=f"uvx --isolated checkov@{CHECKOV_VERSION} --config-file .checkov.yaml",
)

security = project.add_task(
    "security",
    description=(
        "Run all security scanners: dependency audit, secret history, "
        "source patterns, config misconfigurations, IaC policy"
    ),
)
security.spawn(security_sca)
security.spawn(security_sast)
security.spawn(security_secret_scan)
security.spawn(security_misconfig_scan)
security.spawn(security_iac_scan)

# ------------------------------------------------------------------
# Editor integration: ruff as the Python formatter (format on save)
# and the ty language server.
# ------------------------------------------------------------------
vscode = VsCode(project)
vscode.extensions.add_recommendations(
    "charliermarsh.ruff",  # ruff linter and formatter
    "astral-sh.ty",  # ty type checker and language server
)
vscode.settings.add_settings(
    {
        "[python]": {
            "editor.defaultFormatter": "charliermarsh.ruff",
            "editor.formatOnSave": True,
        },
    },
)

github = project.github
if github is None:
    msg = "github workflows should be enabled for this project"
    raise RuntimeError(msg)

SETUP_STEPS: Final = [
    JobStep(uses=CHECKOUT_V4_PIN),
    JobStep(uses=SETUP_UV_V5_PIN, with_={"python-version": PYTHON_VERSION}),
    JobStep(uses=SETUP_NODE_V4_PIN, with_={"node-version": "22"}),
    JobStep(name="Install CDK CLI", run="npm install -g aws-cdk@2.1146.1"),
    JobStep(name="Install dependencies", run="uv sync --frozen"),
]

CHECK_STEPS: Final = [
    JobStep(name="Lint", run=f"{PROJEN_RUN} {lint.name}"),
    JobStep(name="Format check", run=f"{PROJEN_RUN} {format_check.name}"),
    JobStep(name="Type check", run=f"{PROJEN_RUN} {typecheck.name}"),
]

AWS_AUTH_STEPS: Final = [
    JobStep(name="Export constants from constants.py", run=EXPORT_CONSTANTS),
    JobStep(
        name="Configure AWS credentials via OIDC",
        uses=AWS_CREDENTIALS_V4_PIN,
        with_={
            "role-to-assume": "arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/github-actions-deploy",
            "aws-region": "${{ env.AWS_REGION }}",
        },
    ),
]
# Raw cdk diff output is posted verbatim to the PR conversation as a
# single sticky bot comment: `gh pr comment --edit-last
# --create-if-none` refreshes it on every push, and reports no changes
# explicitly since an empty diff yields an empty `cdk-diff.txt`.

POST_CDK_DIFF: Final = """\
DIFF_BODY_FILE=cdk-diff-comment.md
{
  echo '<!-- cdk-diff -->'
  echo '## 📋 cdk diff'
  if [ -s cdk-diff.txt ]; then
    echo '```text'
    cat cdk-diff.txt
    echo '```'
  else
    echo '✅ No infrastructure changes.'
  fi
} > "$DIFF_BODY_FILE"
gh pr comment "${{ github.event.pull_request.number }}" --edit-last --create-if-none --body-file "$DIFF_BODY_FILE"
"""

# ------------------------------------------------------------------
# GitHub Actions: build + synth + tests on every pull request
# ------------------------------------------------------------------
build = github.add_workflow("build")
build.on(pull_request={})
build.add_job(
    "build",
    Job(
        runs_on=["ubuntu-latest"],
        permissions={
            "contents": JobPermission.READ,
            "id_token": JobPermission.WRITE,
            "pull_requests": JobPermission.WRITE,
        },
        steps=[
            *SETUP_STEPS,
            # `--no-post` skips the post-synthesis environment setup
            # (`uv venv --clear` + unfrozen `uv sync` + `uv lock`) that
            # bare `npx projen` runs after synthesizing; it would undo and
            # redo the frozen `uv sync --frozen` install step above.
            JobStep(
                name="Regenerate projen files",
                run=f"{PROJEN_RUN} --no-post --debug",
            ),
            *CHECK_STEPS,
            JobStep(
                name="Unit tests",
                run=f"{PROJEN_RUN} {project.test_task.name}",
            ),
            *AWS_AUTH_STEPS,
            JobStep(
                name="CDK synth",
                run=f"{PROJEN_RUN} {_get_task_by_name('synth').name}",
            ),
            JobStep(
                name="CDK diff",
                run=f"{PROJEN_RUN} {_get_task_by_name('diff').name} > cdk-diff.txt || true",
            ),
            JobStep(
                name="Post CDK diff to PR",
                env={
                    "GH_TOKEN": "${{ github.token }}",
                },
                run=POST_CDK_DIFF,
            ),
            JobStep(
                name="Package",
                run=f"{PROJEN_RUN} {_get_task_by_name('package').name}",
            ),
        ],
    ),
)

# ------------------------------------------------------------------
# GitHub Actions: deploy to the single AWS account on push to main,
# authenticated via OIDC (no long-lived credentials).
# Account/region are read from constants.py - the single source of truth.
# ------------------------------------------------------------------
deploy = github.add_workflow("deploy")
deploy.on(push={"branches": ["main"]}, workflow_dispatch={})
deploy.add_job(
    "deploy",
    Job(
        runs_on=["ubuntu-latest"],
        permissions={
            "id_token": JobPermission.WRITE,
            "contents": JobPermission.READ,
        },
        steps=[
            *SETUP_STEPS,
            *CHECK_STEPS,
            JobStep(
                name="Unit tests",
                run=f"{PROJEN_RUN} {project.test_task.name}",
            ),
            *AWS_AUTH_STEPS,
            JobStep(
                name="CDK diff",
                run=f"{PROJEN_RUN} {_get_task_by_name('diff').name}",
            ),
            JobStep(
                name="Deploy stack",
                run=f"{PROJEN_RUN} {_get_task_by_name('deploy').name}",
            ),
        ],
    ),
)

security = github.add_workflow("security-checks")
security.on(pull_request={}, workflow_dispatch={})

security_permissions: Final = {"contents": JobPermission.READ}

security.add_job(
    "secret-scan",
    Job(
        runs_on=["ubuntu-latest"],
        permissions=security_permissions,
        steps=[
            # Full history: secrets may hide in older commits, not just
            # this PR's diff.
            JobStep(uses=CHECKOUT_V4_PIN, with_={"fetch-depth": "0"}),
            JobStep(
                name="Install gitleaks",
                run=(
                    "curl -fsSL -o /tmp/gitleaks.tar.gz"
                    " "
                    f"https://github.com/gitleaks/gitleaks/releases/download/"
                    f"v{GITLEAKS_VERSION}/"
                    f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz\n"
                    f"printf '%s  %s\\n' {GITLEAKS_LINUX_X64_TARBALL_SHA256}"
                    " /tmp/gitleaks.tar.gz | sha256sum --check --strict -\n"
                    "tar -xzf /tmp/gitleaks.tar.gz -C /tmp\n"
                    "sudo install -m 0755 /tmp/gitleaks /usr/local/bin/gitleaks\n"
                    "gitleaks version"
                ),
            ),
            JobStep(uses=SETUP_NODE_V4_PIN, with_={"node-version": "22"}),
            JobStep(
                name="Secret scan",
                run=f"{PROJEN_RUN} {security_secret_scan.name}",
            ),
        ],
    ),
)

security.add_job(
    "sast",
    Job(
        runs_on=["ubuntu-latest"],
        permissions=security_permissions,
        steps=[
            JobStep(uses=CHECKOUT_V4_PIN),
            JobStep(
                name="Install opengrep",
                run=(
                    "curl -fsSL -o /tmp/opengrep"
                    " "
                    f"https://github.com/opengrep/opengrep/releases/download/v"
                    f"{OPENGREP_VERSION}/opengrep_manylinux_x86\n"
                    f"printf '%s  %s\\n' {OPENGREP_MANYLINUX_X86_SHA256}"
                    " /tmp/opengrep | sha256sum --check --strict -\n"
                    "sudo install -m 0755 /tmp/opengrep /usr/local/bin/opengrep\n"
                    "opengrep --version"
                ),
            ),
            JobStep(uses=SETUP_NODE_V4_PIN, with_={"node-version": "22"}),
            JobStep(
                name="SAST scan",
                run=f"{PROJEN_RUN} {security_sast.name}",
            ),
        ],
    ),
)

security.add_job(
    "misconfig-scan",
    Job(
        runs_on=["ubuntu-latest"],
        permissions=security_permissions,
        steps=[
            JobStep(uses=CHECKOUT_V4_PIN),
            JobStep(
                name="Install trivy",
                run=(
                    "curl -fsSL -o /tmp/trivy.tar.gz"
                    " "
                    "https://github.com/aquasecurity/trivy/releases/download/"
                    f"v{TRIVY_VERSION}/"
                    f"trivy_{TRIVY_VERSION}_Linux-64bit.tar.gz\n"
                    f"printf '%s  %s\\n' {TRIVY_LINUX_64BIT_TARBALL_SHA256}"
                    " /tmp/trivy.tar.gz | sha256sum --check --strict -\n"
                    "tar -xzf /tmp/trivy.tar.gz -C /tmp trivy\n"
                    "sudo install -m 0755 /tmp/trivy /usr/local/bin/trivy\n"
                    "trivy --version"
                ),
            ),
            JobStep(uses=SETUP_NODE_V4_PIN, with_={"node-version": "22"}),
            JobStep(
                name="Misconfig scan",
                run=f"{PROJEN_RUN} {security_misconfig_scan.name}",
            ),
        ],
    ),
)

security.add_job(
    "sca",
    Job(
        runs_on=["ubuntu-latest"],
        permissions=security_permissions,
        steps=[
            JobStep(uses=CHECKOUT_V4_PIN),
            JobStep(
                uses=SETUP_UV_V5_PIN,
                with_={"python-version": PYTHON_VERSION},
            ),
            # No `uv sync` needed: uv audit checks uv.lock directly.
            JobStep(
                name="Dependency audit",
                run=f"{PROJEN_RUN} {security_sca.name}",
            ),
        ],
    ),
)

security.add_job(
    "iac-scan",
    Job(
        runs_on=["ubuntu-latest"],
        permissions=security_permissions,
        steps=[
            *SETUP_STEPS,
            JobStep(
                name="CDK synth",
                run=f"{PROJEN_RUN} {_get_task_by_name('synth:silent').name}",
            ),
            JobStep(
                name="Install scanner",
                run=f"uvx --isolated checkov@{CHECKOV_VERSION} --version",
            ),
            JobStep(
                name="IaC policy scan",
                run=f"{PROJEN_RUN} {security_iac_scan.name}",
            ),
        ],
    ),
)

project.synth()
