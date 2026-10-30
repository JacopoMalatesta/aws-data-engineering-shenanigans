"""Security scanning tasks and tool configuration."""

from typing import Final, TypedDict

from projen import Task, TomlFile, YamlFile
from projen.awscdk import AwsCdkPythonApp

from projenrc.common import ConfigFileSpec

CHECKOV_VERSION: Final = "3.4.0"


SECURITY_CONFIG_FILES: Final[list[ConfigFileSpec]] = [
    {
        "path": "trivy.yaml",
        "kind": "yaml",
        "obj": {
            "severity": ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "scan": {
                "scanners": ["misconfig"],
                "skip-dirs": [".venv", "cdk.out", "node_modules", ".git"],
            },
        },
    },
    {
        "path": ".gitleaks.toml",
        "kind": "toml",
        "obj": {
            "title": "aws-data-engineering-shenanigans gitleaks policy",
            "extend": {"useDefault": True},
        },
    },
    {
        "path": "uv.toml",
        "kind": "toml",
        "obj": {"audit": {"ignore": []}},
    },
    {
        "path": "zizmor.yml",
        "kind": "yaml",
        "obj": {
            "rules": {
                "adhoc-packages": {
                    "ignore": ["build.yml", "deploy.yml", "security.yml"]
                },
                "dangerous-triggers": {"ignore": ["pull-request-lint.yml"]},
            }
        },
    },
    {"path": ".hadolint.yaml", "kind": "yaml", "obj": {}},
    {"path": "osv-scanner.toml", "kind": "toml", "obj": {}},
    {
        "path": ".checkov.yaml",
        "kind": "yaml",
        "obj": {"framework": ["cloudformation"], "directory": "cdk.out"},
    },
]


class SecurityTaskSpec(TypedDict):
    """Specification for a security task."""

    name: str
    description: str
    exec: str


SECURITY_TASK_SPECS: Final[list[SecurityTaskSpec]] = [
    {
        "name": "security:sca-python",
        "description": "Audit uv.lock for known vulnerabilities and deprecated projects",
        "exec": "uv audit --preview-features audit-command",
    },
    {
        "name": "security:sast",
        "description": "Static pattern scan of tracked sources (three rulesets)",
        "exec": (
            "opengrep scan --verbose --config p/security-audit "
            "--config p/owasp-top-ten --config p/python ."
        ),
    },
    {
        "name": "security:secret-scan",
        "description": "Scan the full git history for leaked credentials",
        "exec": "gitleaks detect --no-banner --config .gitleaks.toml",
    },
    {
        "name": "security:misconfig-scan",
        "description": "Misconfiguration scan of the workspace (Dockerfile etc.)",
        "exec": "trivy fs --config trivy.yaml --exit-code 1 .",
    },
    {
        "name": "security:iac-scan",
        "description": "IaC policy scan of the synthesized CloudFormation template (cdk.out)",
        "exec": (
            f"uvx --isolated checkov@{CHECKOV_VERSION} "
            "--config-file .checkov.yaml --show-config"
        ),
    },
    {
        "name": "security:git-hub-actions-scan",
        "description": "Static analysis of GitHub Actions workflows",
        "exec": "zizmor .",
    },
    {
        "name": "security:sca-multi",
        "description": "Scan dependencies for known vulnerabilities (OSV)",
        "exec": "osv-scanner scan source --recursive .",
    },
    {
        "name": "security:dockerfile-lint",
        "description": "Lint Dockerfiles with Hadolint",
        "exec": (
            "find . -name 'Dockerfile*' -not -path './.venv/*' "
            "-not -path '*/node_modules/*' -exec hadolint {} +"
        ),
    },
]


class SecurityTasks(TypedDict):
    """Tasks created by :func:`create_security`."""

    sca_python: Task
    sast: Task
    secret_scan: Task
    misconfig_scan: Task
    iac_scan: Task
    git_hub_actions_scan: Task
    sca_multi: Task
    dockerfile_lint: Task
    security: Task


def create_security(project: AwsCdkPythonApp) -> SecurityTasks:
    """Create security scanner config files and security tasks.

    Args:
        project: The projen project.

    Returns:
        The created security tasks.
    """
    for spec in SECURITY_CONFIG_FILES:
        if spec["kind"] == "yaml":
            YamlFile(project, spec["path"], obj=spec["obj"])
        else:
            TomlFile(project, spec["path"], obj=spec["obj"])

    tasks: dict[str, Task] = {}
    for spec in SECURITY_TASK_SPECS:
        tasks[spec["name"]] = project.add_task(
            spec["name"],
            description=spec["description"],
            exec=spec["exec"],
        )

    security = project.add_task(
        "security",
        description=(
            "Run all security scanners: dependency audit, secret history, "
            "source patterns, config misconfigurations, IaC policy"
        ),
    )
    for task in tasks.values():
        security.spawn(task)

    return SecurityTasks(
        sca_python=tasks["security:sca-python"],
        sast=tasks["security:sast"],
        secret_scan=tasks["security:secret-scan"],
        misconfig_scan=tasks["security:misconfig-scan"],
        iac_scan=tasks["security:iac-scan"],
        git_hub_actions_scan=tasks["security:git-hub-actions-scan"],
        sca_multi=tasks["security:sca-multi"],
        dockerfile_lint=tasks["security:dockerfile-lint"],
        security=security,
    )
