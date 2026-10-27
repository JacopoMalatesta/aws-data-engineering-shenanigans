"""Projen project definition - the single source of truth for this repo.

Edit this file, then re-run it (``npx projen``) to regenerate every
projen-managed file. Never hand-edit those; they are read-only.
"""

from projen.awscdk import AwsCdkPythonApp
from projen.github.workflows import Job, JobPermission, JobStep
from projen.vscode import VsCode

project = AwsCdkPythonApp(
    author_email="jacopomalatesta95@gmail.com",
    author_name="JacopoMalatesta",
    cdk_version="2.275.0",
    # Exact pins: ty is pre-1.0 (unstable API) and ruff's rule set
    # evolves, so both are pinned rather than ranged.
    dev_deps=["ruff@0.17.2", "ty@0.0.92"],
    module_name="aws_data_engineering_shenanigans",
    name="aws-data-engineering-shenanigans",
    uv=True,
    # Pin the venv to CPython 3.13 (uv fetches it automatically) and pin
    # requires-python in pyproject.toml accordingly.
    uv_options={
        "python_exec": "3.13",
        "project": {
            "name": "aws-data-engineering-shenanigans",
            "requires_python": ">=3.13,<4.0",
        },
    },
    version="0.1.0",
)

# Local OpenCode helper scripts are not part of the repo.
project.add_git_ignore(".opencode/")

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

# Gate the build: projen locks the "build" task after construction
# ("do not allow additional build phases"), so the checks are spawned
# from the unlocked "test" task instead - they run after pytest and
# before packaging in the build chain.
test_task = project.test_task
test_task.spawn(lint)
test_task.spawn(format_check)
test_task.spawn(typecheck)

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

# ------------------------------------------------------------------
# GitHub Actions: build + synth + tests on every pull request
# ------------------------------------------------------------------
github = project.github
if github is None:
    msg = "github workflows should be enabled for this project"
    raise RuntimeError(msg)

build = github.add_workflow("build")
build.on(pull_request={})
build.add_job(
    "build",
    Job(
        runs_on=["ubuntu-latest"],
        permissions={"contents": JobPermission.READ},
        steps=[
            JobStep(uses="actions/checkout@v4"),
            JobStep(uses="astral-sh/setup-uv@v5", with_={"python-version": "3.13"}),
            JobStep(uses="actions/setup-node@v4", with_={"node-version": "22"}),
            JobStep(name="Install CDK CLI", run="npm install -g aws-cdk@2.1146.1"),
            JobStep(name="Install dependencies", run="uv sync --frozen"),
            JobStep(name="Build, synth and test", run="npx projen@0.104.17 build"),
        ],
    ),
)

# ------------------------------------------------------------------
# GitHub Actions: deploy to the single AWS account on push to main,
# authenticated via OIDC (no long-lived credentials).
# Account/region are read from constants.py - the single source of truth.
# ------------------------------------------------------------------
EXPORT_CONSTANTS = """echo "AWS_ACCOUNT_ID=$(uv run python -c 'from constants import AWS_ACCOUNT_ID; print(AWS_ACCOUNT_ID)')" >> "$GITHUB_ENV"
echo "AWS_REGION=$(uv run python -c 'from constants import AWS_REGION; print(AWS_REGION)')" >> "$GITHUB_ENV"
"""

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
            JobStep(uses="actions/checkout@v4"),
            JobStep(uses="astral-sh/setup-uv@v5", with_={"python-version": "3.13"}),
            JobStep(uses="actions/setup-node@v4", with_={"node-version": "22"}),
            JobStep(name="Install CDK CLI", run="npm install -g aws-cdk@2.1146.1"),
            JobStep(name="Install dependencies", run="uv sync --frozen"),
            JobStep(name="Lint", run="npx projen@0.104.17 lint"),
            JobStep(name="Format check", run="npx projen@0.104.17 format:check"),
            JobStep(name="Type check", run="npx projen@0.104.17 typecheck"),
            JobStep(name="Unit tests", run="npx projen@0.104.17 test"),
            JobStep(name="Export constants from constants.py", run=EXPORT_CONSTANTS),
            JobStep(
                name="Configure AWS credentials via OIDC",
                uses="aws-actions/configure-aws-credentials@v4",
                with_={
                    "role-to-assume": "arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/github-actions-deploy",
                    "aws-region": "${{ env.AWS_REGION }}",
                },
            ),
            JobStep(name="Deploy stack", run="npx projen@0.104.17 deploy"),
        ],
    ),
)

project.synth()
