from projen.awscdk import AwsCdkPythonApp
from projen.github.workflows import Job, JobPermission, JobStep

project = AwsCdkPythonApp(
    author_email="jacopomalatesta95@gmail.com",
    author_name="JacopoMalatesta",
    cdk_version="2.275.0",
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
# GitHub Actions: build + synth + tests on every pull request
# ------------------------------------------------------------------
build = project.github.add_workflow("build")
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
EXPORT_CONSTANTS = "\n".join(
    [
        'echo "AWS_ACCOUNT_ID=$(uv run python -c \'from constants import AWS_ACCOUNT_ID; print(AWS_ACCOUNT_ID)\')" >> "$GITHUB_ENV"',
        'echo "AWS_REGION=$(uv run python -c \'from constants import AWS_REGION; print(AWS_REGION)\')" >> "$GITHUB_ENV"',
    ]
)

deploy = project.github.add_workflow("deploy")
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
