"""GitHub Actions workflows."""

from typing import Final, Literal, NotRequired, TypedDict

from projen.awscdk import AwsCdkPythonApp
from projen.github import GithubWorkflow
from projen.github.workflows import Job, JobPermission, JobStep

from projenrc.checks import ChecksTasks
from projenrc.common import PROJEN_VERSION, PYTHON_VERSION, JsonValue, get_task_by_name
from projenrc.security import CHECKOV_VERSION, SecurityTasks

# Cross-cutting CI constants.
CI_RUNNER: Final = "ubuntu-latest"
NODE_VERSION: Final = "24"
CDK_CLI_VERSION: Final = "2.1146.1"
PROJEN_RUN: Final = f"npx projen@{PROJEN_VERSION}"

# Action pins.
CHECKOUT_V4_PIN: Final = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
SETUP_UV_V5_PIN: Final = "astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86"
SETUP_NODE_V4_PIN: Final = "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020"
AWS_CREDENTIALS_V4_PIN: Final = (
    "aws-actions/configure-aws-credentials@7474bc4690e29a8392af63c5b98e7449536d5c3a"
)

EXPORT_CONSTANTS: Final = (
    'echo "AWS_ACCOUNT_ID=$(uv run python -c '
    '\'from constants import AWS_ACCOUNT_ID; print(AWS_ACCOUNT_ID)\')" >> "$GITHUB_ENV"\n'
    'echo "AWS_REGION=$(uv run python -c '
    '\'from constants import AWS_REGION; print(AWS_REGION)\')" >> "$GITHUB_ENV"\n'
)

# Security scanner pins.
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
ZIZMOR_VERSION: Final = "1.31.1"
OSV_SCANNER_VERSION: Final = "2.7.0"
HADOLINT_VERSION: Final = "2.15.1"
ZIZMOR_LINUX_X64_TARBALL_SHA256: Final = (
    "d185f726bdaf92df78273217dfdd24ebcd6b0ef48cf3ce776ff5762b6e138c99"
)
OSV_SCANNER_LINUX_AMD64_SHA256: Final = (
    "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b"
)
HADOLINT_LINUX_X86_64_SHA256: Final = (
    "c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507"
)

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
gh pr comment "$PR_NUMBER" --edit-last --create-if-none --body-file "$DIFF_BODY_FILE"
"""


SCANNER_DOWNLOAD_SPECS: Final[dict[str, "ScannerDownloadSpec"]] = {
    "gitleaks": {
        "name": "Secret scan",
        "version": GITLEAKS_VERSION,
        "sha256": GITLEAKS_LINUX_X64_TARBALL_SHA256,
        "url": (
            "https://github.com/gitleaks/gitleaks/releases/download/"
            f"v{GITLEAKS_VERSION}/"
            f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz"
        ),
        "binary": "gitleaks",
        "kind": "tarball",
        "version_command": "gitleaks version",
        "archive_member": None,
    },
    "opengrep": {
        "name": "SAST scan",
        "version": OPENGREP_VERSION,
        "sha256": OPENGREP_MANYLINUX_X86_SHA256,
        "url": (
            "https://github.com/opengrep/opengrep/releases/download/"
            f"v{OPENGREP_VERSION}/opengrep_manylinux_x86"
        ),
        "binary": "opengrep",
        "kind": "binary",
        "version_command": "opengrep --version",
        "archive_member": None,
    },
    "trivy": {
        "name": "Misconfig scan",
        "version": TRIVY_VERSION,
        "sha256": TRIVY_LINUX_64BIT_TARBALL_SHA256,
        "url": (
            "https://github.com/aquasecurity/trivy/releases/download/"
            f"v{TRIVY_VERSION}/"
            f"trivy_{TRIVY_VERSION}_Linux-64bit.tar.gz"
        ),
        "binary": "trivy",
        "kind": "tarball",
        "version_command": "trivy --version",
        "archive_member": "trivy",
    },
    "zizmor": {
        "name": "GitHub Actions scan",
        "version": ZIZMOR_VERSION,
        "sha256": ZIZMOR_LINUX_X64_TARBALL_SHA256,
        "url": (
            "https://github.com/zizmorcore/zizmor/releases/download/"
            f"v{ZIZMOR_VERSION}/"
            "zizmor-x86_64-unknown-linux-gnu.tar.gz"
        ),
        "binary": "zizmor",
        "kind": "tarball",
        "version_command": "zizmor --version",
        "archive_member": None,
    },
    "osv": {
        "name": "SCA (multi)",
        "version": OSV_SCANNER_VERSION,
        "sha256": OSV_SCANNER_LINUX_AMD64_SHA256,
        "url": (
            "https://github.com/google/osv-scanner/releases/download/"
            f"v{OSV_SCANNER_VERSION}/osv-scanner_linux_amd64"
        ),
        "binary": "osv-scanner",
        "kind": "binary",
        "version_command": "osv-scanner --version",
        "archive_member": None,
    },
    "hadolint": {
        "name": "Dockerfile scan",
        "version": HADOLINT_VERSION,
        "sha256": HADOLINT_LINUX_X86_64_SHA256,
        "url": (
            "https://github.com/hadolint/hadolint/releases/download/"
            f"v{HADOLINT_VERSION}/hadolint-linux-x86_64"
        ),
        "binary": "hadolint",
        "kind": "binary",
        "version_command": "hadolint --version",
        "archive_member": None,
    },
}


class JobStepSpec(TypedDict):
    """Declarative specification for a GitHub Actions job step."""

    name: str
    background: NotRequired[bool]
    env: NotRequired[dict[str, str]]
    run: NotRequired[str]
    uses: NotRequired[str]
    with_: NotRequired[dict[str, JsonValue]]
    wait_all: NotRequired[bool]


SETUP_STEP_SPECS: Final[list[JobStepSpec]] = [
    {
        "name": "Checkout",
        "uses": CHECKOUT_V4_PIN,
        "with_": {"persist-credentials": False},
    },
    {
        "name": "Setup uv",
        "uses": SETUP_UV_V5_PIN,
        "with_": {"python-version": PYTHON_VERSION},
    },
    {
        "name": "Setup Node",
        "uses": SETUP_NODE_V4_PIN,
        "with_": {"node-version": NODE_VERSION},
    },
    {"name": "Install CDK CLI", "run": f"npm install -g aws-cdk@{CDK_CLI_VERSION}"},
    {"name": "Install dependencies", "run": "uv sync --frozen"},
    {"name": "Install projen CLI", "run": f"npm install -g projen@{PROJEN_VERSION}"},
]

AWS_AUTH_STEP_SPECS: Final[list[JobStepSpec]] = [
    {"name": "Export constants from constants.py", "run": EXPORT_CONSTANTS},
    {
        "name": "Configure AWS credentials via OIDC",
        "uses": AWS_CREDENTIALS_V4_PIN,
        "with_": {
            "role-to-assume": "arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/github-actions-deploy",
            "aws-region": "${{ env.AWS_REGION }}",
        },
    },
]


class ScannerDownloadSpec(TypedDict):
    """Specification for a downloaded security scanner."""

    name: str
    version: str
    sha256: str
    url: str
    binary: str
    kind: Literal["tarball", "binary"]
    version_command: str
    archive_member: str | None


def tarball_scanner_run(spec: ScannerDownloadSpec) -> str:
    """Build the run script for a tarball-packaged scanner.

    Returns:
        The generated shell script.
    """
    member = spec["archive_member"]
    tar_command = (
        f"tar -xzf /tmp/{spec['binary']}.tar.gz -C /tmp {member}\n"
        if member is not None
        else f"tar -xzf /tmp/{spec['binary']}.tar.gz -C /tmp\n"
    )
    return (
        f"curl -fsSL -o /tmp/{spec['binary']}.tar.gz {spec['url']}\n"
        f"printf '%s  %s\\n' {spec['sha256']} "
        f"/tmp/{spec['binary']}.tar.gz | sha256sum --check --strict -\n"  # ruff: ignore[hardcoded-temp-file]
        + tar_command
        + f"sudo install -m 0755 /tmp/{spec['binary']} "
        f"/usr/local/bin/{spec['binary']}\n"
        f"{spec['version_command']}\n"
    )


def binary_scanner_run(spec: ScannerDownloadSpec) -> str:
    """Build the run script for a single-binary scanner.

    Returns:
        The generated shell script.
    """
    return (
        f"curl -fsSL -o /tmp/{spec['binary']} {spec['url']}\n"
        f"printf '%s  %s\\n' {spec['sha256']} "
        f"/tmp/{spec['binary']} | sha256sum --check --strict -\n"  # ruff: ignore[hardcoded-temp-file]
        f"sudo install -m 0755 /tmp/{spec['binary']} "
        f"/usr/local/bin/{spec['binary']}\n"
        f"{spec['version_command']}\n"
    )


class Workflows(TypedDict):
    """Workflows created by :func:`create_workflows`."""

    build: GithubWorkflow
    deploy: GithubWorkflow
    security: GithubWorkflow


def create_workflows(
    project: AwsCdkPythonApp,
    *,
    checks_tasks: ChecksTasks,
    security_tasks: SecurityTasks,
) -> Workflows:
    """Create the build, deploy, and security GitHub workflows.

    Returns:
        The created workflows.

    Raises:
        RuntimeError: If GitHub workflows are not enabled.
    """
    github = project.github
    if github is None:
        msg = "github workflows should be enabled for this project"
        raise RuntimeError(msg)

    check_step_specs: list[JobStepSpec] = [
        {"name": "Lint", "run": f"{PROJEN_RUN} {checks_tasks['lint'].name}"},
        {
            "name": "Format check",
            "run": f"{PROJEN_RUN} {checks_tasks['format_check'].name}",
        },
        {"name": "Type check", "run": f"{PROJEN_RUN} {checks_tasks['typecheck'].name}"},
    ]
    setup_steps = [
        JobStep(
            name=spec["name"],
            background=spec.get("background"),
            env=spec.get("env"),
            run=spec.get("run"),
            uses=spec.get("uses"),
            with_=spec.get("with_"),
            wait_all=spec.get("wait_all"),
        )
        for spec in SETUP_STEP_SPECS
    ]

    security_scan_step_specs: list[JobStepSpec] = [
        {
            "name": "Secret scan",
            "background": True,
            "run": (
                'if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then\n'
                "  git fetch --unshallow\n"
                "fi\n"
                + tarball_scanner_run(SCANNER_DOWNLOAD_SPECS["gitleaks"])
                + f"{PROJEN_RUN} {security_tasks['secret_scan'].name}"
            ),
        },
        {
            "name": "SAST scan",
            "background": True,
            "run": (
                binary_scanner_run(SCANNER_DOWNLOAD_SPECS["opengrep"])
                + f"{PROJEN_RUN} {security_tasks['sast'].name}"
            ),
        },
        {
            "name": "Misconfig scan",
            "background": True,
            "run": (
                tarball_scanner_run(SCANNER_DOWNLOAD_SPECS["trivy"])
                + f"{PROJEN_RUN} {security_tasks['misconfig_scan'].name}"
            ),
        },
        {
            "name": "SCA (Python)",
            "background": True,
            "run": f"{PROJEN_RUN} {security_tasks['sca_python'].name}",
        },
        {
            "name": "IaC scan",
            "background": True,
            "run": (
                f"{PROJEN_RUN} {get_task_by_name(project, 'synth:silent').name}\n"
                f"uvx --isolated checkov@{CHECKOV_VERSION} --version\n"
                f"{PROJEN_RUN} {security_tasks['iac_scan'].name}"
            ),
        },
        {
            "name": "GitHub Actions scan",
            "background": True,
            "run": (
                tarball_scanner_run(SCANNER_DOWNLOAD_SPECS["zizmor"])
                + f"{PROJEN_RUN} {security_tasks['git_hub_actions_scan'].name}"
            ),
        },
        {
            "name": "SCA (multi)",
            "background": True,
            "run": (
                binary_scanner_run(SCANNER_DOWNLOAD_SPECS["osv"])
                + f"{PROJEN_RUN} {security_tasks['sca_multi'].name}"
            ),
        },
        {
            "name": "Dockerfile scan",
            "background": True,
            "run": (
                binary_scanner_run(SCANNER_DOWNLOAD_SPECS["hadolint"])
                + f"{PROJEN_RUN} {security_tasks['dockerfile_lint'].name}"
            ),
        },
    ]
    build_step_specs: list[JobStepSpec] = [
        *SETUP_STEP_SPECS,
        {
            "name": "Regenerate projen files",
            "run": f"{PROJEN_RUN} --no-post --debug",
        },
        *check_step_specs,
        {
            "name": "Unit tests",
            "run": f"{PROJEN_RUN} {project.test_task.name}",
        },
        *AWS_AUTH_STEP_SPECS,
        {
            "name": "CDK synth",
            "run": f"{PROJEN_RUN} {get_task_by_name(project, 'synth').name}",
        },
        {
            "name": "CDK diff",
            "run": (
                f"{PROJEN_RUN} {get_task_by_name(project, 'diff').name} "
                "> cdk-diff.txt || true"
            ),
        },
        {
            "name": "Post CDK diff to PR",
            "env": {
                "GH_TOKEN": "${{ github.token }}",
                "PR_NUMBER": "${{ github.event.pull_request.number }}",
            },
            "run": POST_CDK_DIFF,
        },
        {
            "name": "Package",
            "run": f"{PROJEN_RUN} {get_task_by_name(project, 'package').name}",
        },
    ]

    build = github.add_workflow("build")
    build.on(pull_request={})
    build.add_job(
        "build",
        Job(
            runs_on=[CI_RUNNER],
            permissions={
                "contents": JobPermission.READ,
                "id_token": JobPermission.WRITE,
                "pull_requests": JobPermission.WRITE,
            },
            steps=[
                JobStep(
                    name=spec["name"],
                    background=spec.get("background"),
                    env=spec.get("env"),
                    run=spec.get("run"),
                    uses=spec.get("uses"),
                    with_=spec.get("with_"),
                    wait_all=spec.get("wait_all"),
                )
                for spec in build_step_specs
            ],
        ),
    )

    deploy_step_specs: list[JobStepSpec] = [
        *SETUP_STEP_SPECS,
        *check_step_specs,
        {
            "name": "Unit tests",
            "run": f"{PROJEN_RUN} {project.test_task.name}",
        },
        *AWS_AUTH_STEP_SPECS,
        {
            "name": "CDK diff",
            "run": f"{PROJEN_RUN} {get_task_by_name(project, 'diff').name}",
        },
        {
            "name": "Deploy stack",
            "run": f"{PROJEN_RUN} {get_task_by_name(project, 'deploy').name}",
        },
    ]

    deploy = github.add_workflow("deploy")
    deploy.on(push={"branches": ["main"]}, workflow_dispatch={})
    deploy.add_job(
        "deploy",
        Job(
            runs_on=[CI_RUNNER],
            permissions={
                "id_token": JobPermission.WRITE,
                "contents": JobPermission.READ,
            },
            steps=[
                JobStep(
                    name=spec["name"],
                    background=spec.get("background"),
                    env=spec.get("env"),
                    run=spec.get("run"),
                    uses=spec.get("uses"),
                    with_=spec.get("with_"),
                    wait_all=spec.get("wait_all"),
                )
                for spec in deploy_step_specs
            ],
        ),
    )

    security_workflow = github.add_workflow("security")
    security_workflow.on(pull_request={}, workflow_dispatch={})

    security_workflow.add_job(
        "scan",
        Job(
            runs_on=[CI_RUNNER],
            permissions={"contents": JobPermission.READ},
            steps=[
                *setup_steps,
                *[
                    JobStep(
                        name=spec["name"],
                        background=spec.get("background"),
                        env=spec.get("env"),
                        run=spec.get("run"),
                        uses=spec.get("uses"),
                        with_=spec.get("with_"),
                        wait_all=spec.get("wait_all"),
                    )
                    for spec in security_scan_step_specs
                ],
                JobStep(wait_all=True),
            ],
        ),
    )

    return Workflows(build=build, deploy=deploy, security=security_workflow)
