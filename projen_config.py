"""Project configuration data consumed by ``.projenrc.py`` and ``app.py``.

This module stores configuration only. It never creates projen resources.
"""

from typing import Final, TypedDict, cast

from aws_cdk.region_info import RegionInfo

from constants import (
    AIRFLOW_RUFF_RULESET,
    AWS_CREDENTIALS_V4_PIN,
    CHECKOUT_V4_PIN,
    CHECKOV_VERSION,
    DJANGO_RUFF_RULESET,
    FASTAPI_RUFF_RULESET,
    GITLEAKS_LINUX_X64_TARBALL_SHA256,
    GITLEAKS_VERSION,
    HADOLINT_LINUX_X86_64_SHA256,
    HADOLINT_VERSION,
    NODE_VERSION,
    NUMPY_RUFF_RULESET,
    OPENGREP_MANYLINUX_X86_SHA256,
    OPENGREP_VERSION,
    OSV_SCANNER_LINUX_AMD64_SHA256,
    OSV_SCANNER_VERSION,
    PANDAS_RUFF_RULESET,
    POST_CDK_DIFF,
    PRE_COMMIT_LANGUAGE_UNSUPPORTED,
    PROJEN_RUN,
    PYTHON_VERSION,
    SETUP_NODE_V4_PIN,
    SETUP_UV_V5_PIN,
    TRIVY_LINUX_64BIT_TARBALL_SHA256,
    TRIVY_VERSION,
    VIRTUAL_ENV_BINARY_DIR,
    ZIZMOR_LINUX_X64_TARBALL_SHA256,
    ZIZMOR_VERSION,
)
from projen_types import (
    DeploymentEnvironment,
    EnvironmentName,
    FileSpec,
    FileType,
    GitHubJobSpec,
    GitHubJobStepSpec,
    GitHubPermission,
    GitHubWorkflowSpec,
    JobName,
    JobStepName,
    JsonValue,
    PreCommitHookSpec,
    ProjenTaskSpec,
    TaskName,
    WorkflowName,
)

GIT_IGNORE_PATTERNS: Final = ["*.swp", ".opencode/", "tmp/"]

SEMANTIC_TITLE_TYPES: Final = [
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
]

VSCODE_EXTENSIONS: Final = [
    "astral-sh.ty",
    "charliermarsh.ruff",
    "detachhead.basedpyright",
]

VSCODE_SETTINGS: Final[dict[str, JsonValue]] = {
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": True,
    },
}

DEV_DEPS: Final = [
    "basedpyright@1.40.2",
    "pre-commit@4.6.2",
    "ruff@0.17.2",
    "ty@0.0.92",
]


class ProjectSpec(TypedDict):
    """Identity metadata of the ``AwsCdkPythonApp`` project."""

    name: str
    module_name: str
    author_name: str
    author_email: str
    version: str
    cdk_version: str
    pytest_version: str


PROJECT_SPEC: Final[ProjectSpec] = {
    "name": "aws-data-engineering-shenanigans",
    "module_name": "aws_data_engineering_shenanigans",
    "author_name": "JacopoMalatesta",
    "author_email": "jacopomalatesta95@gmail.com",
    "version": "0.1.0",
    "cdk_version": "2.275.0",
    "pytest_version": "9.0.3",
}

RUFF_IGNORE_RULES: Final = [
    AIRFLOW_RUFF_RULESET,
    DJANGO_RUFF_RULESET,
    FASTAPI_RUFF_RULESET,
    NUMPY_RUFF_RULESET,
    PANDAS_RUFF_RULESET,
    "avoidable-escaped-quote",
    "bad-quotes-docstring",
    "bad-quotes-inline-string",
    "bad-quotes-multiline-string",
    "docstring-tab-indentation",
    "incorrect-blank-line-before-class",
    "indentation-with-invalid-multiple",
    "indentation-with-invalid-multiple-comment",
    "line-too-long",
    "missing-copyright-notice",
    "missing-trailing-comma",
    "multi-line-implicit-string-concatenation",
    "over-indented",
    "prohibited-trailing-comma",
    "tab-indentation",
    "triple-single-quotes",
]

RUFF_PER_FILE_IGNORES: Final[dict[str, list[str]]] = {
    "tests/**": [
        "assert",
        "undocumented-public-class",
        "undocumented-public-function",
        "undocumented-public-method",
        "undocumented-public-module",
        "undocumented-public-package",
    ],
    "**/__init__.py": ["undocumented-public-package"],
}

PROJEN_TASKS: Final[list[ProjenTaskSpec]] = [
    {
        "name": TaskName.PYTHON_LINT,
        "description": "Lint with ruff",
        "exec": "ruff check .",
    },
    {
        "name": TaskName.PYTHON_LINT_FIX,
        "description": "Autofix ruff violations (safe fixes only)",
        "exec": "ruff check --fix .",
    },
    {
        "name": TaskName.PYTHON_FORMAT,
        "description": "Format code with ruff",
        "exec": "ruff format .",
    },
    {
        "name": TaskName.PYTHON_FORMAT_CHECK,
        "description": "Verify ruff formatting",
        "exec": "ruff format --check .",
    },
    {
        "name": TaskName.PYTHON_STATIC_ANALYSIS,
        "description": "Static analysis with basedpyright",
        "exec": "basedpyright",
    },
    {
        "name": TaskName.PYTHON_TYPECHECK,
        "description": "Type check with ty",
        "exec": "ty check --error-on-warning .",
    },
    {
        "name": TaskName.PYTHON_CHECK,
        "description": "Run all static checks: lint, format check, type check",
        "spawns": [
            TaskName.PYTHON_LINT,
            TaskName.PYTHON_FORMAT_CHECK,
            TaskName.PYTHON_TYPECHECK,
            TaskName.PYTHON_STATIC_ANALYSIS,
        ],
    },
    {
        "name": TaskName.SECURITY_SCA_PYTHON,
        "description": "Audit uv.lock for known vulnerabilities and deprecated projects",
        "exec": "uv audit --preview-features audit-command",
    },
    {
        "name": TaskName.SECURITY_SAST,
        "description": "Static pattern scan of tracked sources (three rulesets)",
        "exec": (
            "opengrep scan --verbose --config p/security-audit --config p/owasp-top-ten"
            " --config p/python ."
        ),
    },
    {
        "name": TaskName.SECURITY_SECRET_SCAN,
        "description": "Scan the full git history for leaked credentials",
        "exec": "gitleaks detect --no-banner --config .gitleaks.toml",
    },
    {
        "name": TaskName.SECURITY_MISCONFIG_SCAN,
        "description": "Misconfiguration scan of the workspace (Dockerfile etc.)",
        "exec": "trivy fs --config trivy.yaml --exit-code 1 .",
    },
    {
        "name": TaskName.SECURITY_IAC_SCAN,
        "description": "IaC policy scan of the synthesized CloudFormation template (cdk.out)",
        "exec": f"uvx --isolated checkov@{CHECKOV_VERSION} --config-file .checkov.yaml --show-config",
    },
    {
        "name": TaskName.SECURITY_GITHUB_ACTIONS_SCAN,
        "description": "Static analysis of GitHub Actions workflows",
        "exec": "zizmor .",
    },
    {
        "name": TaskName.SECURITY_SCA_MULTI_LANGUAGE,
        "description": "Scan dependencies for known vulnerabilities (OSV)",
        "exec": "osv-scanner scan source --recursive .",
    },
    {
        "name": TaskName.SECURITY_DOCKERFILE_LINT,
        "description": "Lint Dockerfiles with Hadolint",
        "exec": (
            "find . -name 'Dockerfile*' -not -path './.venv/*' "
            "-not -path '*/node_modules/*' -exec hadolint {} +"
        ),
    },
    {
        "name": TaskName.SECURITY,
        "description": (
            "Run all security scanners: dependency audit, secret history, "
            "source patterns, config misconfigurations, IaC policy"
        ),
        "spawns": [
            TaskName.SECURITY_SCA_PYTHON,
            TaskName.SECURITY_SAST,
            TaskName.SECURITY_SECRET_SCAN,
            TaskName.SECURITY_MISCONFIG_SCAN,
            TaskName.SECURITY_IAC_SCAN,
            TaskName.SECURITY_GITHUB_ACTIONS_SCAN,
            TaskName.SECURITY_SCA_MULTI_LANGUAGE,
            TaskName.SECURITY_DOCKERFILE_LINT,
        ],
    },
]

PRE_COMMIT_HOOKS: Final[list[PreCommitHookSpec]] = [
    {
        "id": "ruff-lint-fix",
        "name": "ruff check --fix",
        "entry": f"{VIRTUAL_ENV_BINARY_DIR}ruff",
        "args": ["check", "--fix"],
        "language": PRE_COMMIT_LANGUAGE_UNSUPPORTED,
        "types_or": ["python", "pyi"],
    },
    {
        "id": "ruff-format",
        "name": "ruff format",
        "entry": f"{VIRTUAL_ENV_BINARY_DIR}ruff",
        "args": ["format"],
        "language": PRE_COMMIT_LANGUAGE_UNSUPPORTED,
        "types_or": ["python", "pyi"],
    },
    {
        "id": "ty-check",
        "name": "ty check",
        "entry": f"{VIRTUAL_ENV_BINARY_DIR}ty",
        "args": ["check", "--error-on-warning", "."],
        "language": PRE_COMMIT_LANGUAGE_UNSUPPORTED,
        "pass_filenames": False,
        "files": r"\.py$",
    },
    {
        "id": "basedpyright-check",
        "name": "basedpyright",
        "entry": f"{VIRTUAL_ENV_BINARY_DIR}basedpyright",
        "args": [],
        "language": PRE_COMMIT_LANGUAGE_UNSUPPORTED,
        "pass_filenames": False,
        "files": r"\.py$",
    },
]

PROJECT_FILES: Final[list[FileSpec]] = [
    {
        "file_path": "ruff.toml",
        "file_type": FileType.TOML,
        "obj": {
            "target-version": f"py{PYTHON_VERSION.replace('.', '')}",
            "line-length": 88,
            "lint": cast(
                "JsonValue",
                {
                    "preview": True,
                    "select": ["ALL"],
                    "ignore": RUFF_IGNORE_RULES,
                    "pydocstyle": {"convention": "google"},
                    "per-file-ignores": RUFF_PER_FILE_IGNORES,
                },
            ),
        },
    },
    {
        "file_path": "ty.toml",
        "file_type": FileType.TOML,
        "obj": {
            "rules": {
                "blanket-ignore-comment": "error",
                "dynamic-function-decorator-return": "error",
                "missing-type-argument": "error",
                "possibly-unresolved-reference": "warn",
                "unsound-assignment": "error",
                "unsound-return-statement": "error",
                "unsound-yield": "error",
                "unsupported-dynamic-base": "warn",
            },
            "analysis": {
                "strict-equality-semantics": True,
                "strict-generic-narrowing": True,
            },
        },
    },
    {
        "file_path": "pyrightconfig.json",
        "file_type": FileType.JSON,
        "marker": False,
        "obj": {
            "pythonVersion": PYTHON_VERSION,
            "pythonPlatform": "All",
            "typeCheckingMode": "all",
            "enableBasedFeatures": True,
            "failOnWarnings": True,
            "exclude": [
                "cdk.out",
                "dist",
                ".venv",
                "node_modules",
                "**/__pycache__",
            ],
        },
    },
    {
        "file_path": ".pre-commit-config.yaml",
        "file_type": FileType.YAML,
        "obj": {
            "repos": [
                {
                    "repo": "local",
                    "hooks": cast("list[JsonValue]", PRE_COMMIT_HOOKS),
                }
            ]
        },
    },
    {
        "file_path": "trivy.yaml",
        "file_type": FileType.YAML,
        "obj": {
            "severity": ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "scan": {
                "scanners": ["misconfig"],
                "skip-dirs": [".venv", "cdk.out", "node_modules", ".git"],
            },
        },
    },
    {
        "file_path": ".gitleaks.toml",
        "file_type": FileType.TOML,
        "obj": {
            "title": "aws-data-engineering-shenanigans gitleaks policy",
            "extend": {"useDefault": True},
        },
    },
    {
        "file_path": "uv.toml",
        "file_type": FileType.TOML,
        "obj": {"audit": {"ignore": []}},
    },
    {
        "file_path": "zizmor.yml",
        "file_type": FileType.YAML,
        "obj": {
            "rules": {
                "adhoc-packages": {
                    "ignore": ["build.yml", "deploy.yml", "security.yml"]
                },
                "dangerous-triggers": {"ignore": ["pull-request-lint.yml"]},
            }
        },
    },
    {
        "file_path": ".hadolint.yaml",
        "file_type": FileType.YAML,
        "obj": {},
    },
    {
        "file_path": "osv-scanner.toml",
        "file_type": FileType.TOML,
        "obj": {},
    },
    {
        "file_path": ".checkov.yaml",
        "file_type": FileType.YAML,
        "obj": {"framework": ["cloudformation"], "directory": "cdk.out"},
    },
]

DEPLOYMENT_ENVIRONMENTS: Final[list[DeploymentEnvironment]] = [
    {
        "environment_name": EnvironmentName.DEV,
        "aws_account_id": "925000840053",
        "region_name": RegionInfo.get("eu-west-1").name,
    },
]

CI_RUNNERS: Final = ["ubuntu-latest"]

GITHUB_JOB_STEPS: Final[list[GitHubJobStepSpec]] = [
    {
        "name": JobStepName.AWS_CREDENTIALS,
        "uses": AWS_CREDENTIALS_V4_PIN,
        "with_": {
            "role-to-assume": "arn:aws:iam::${{ matrix.aws_account_id }}:role/github-actions-deploy",
            "aws-region": "${{ matrix.region_name }}",
        },
    },
    {
        "name": JobStepName.CDK_DEPLOY,
        "run": f'{PROJEN_RUN} deploy "*-${{{{ matrix.environment_name }}}}"',
    },
    {"name": JobStepName.CDK_DIFF, "run": f"{PROJEN_RUN} {TaskName.CDK_DIFF}"},
    {
        "name": JobStepName.CDK_DIFF_CAPTURE,
        "run": f"{PROJEN_RUN} {TaskName.CDK_DIFF} > cdk-diff.txt || true",
    },
    {"name": JobStepName.CDK_SYNTH, "run": f"{PROJEN_RUN} {TaskName.CDK_SYNTH}"},
    {
        "name": JobStepName.CHECKOUT,
        "uses": CHECKOUT_V4_PIN,
        "with_": {"persist-credentials": False},
    },
    {
        "name": JobStepName.DOCKERFILE_SCAN,
        "background": True,
        "run": (
            "curl -fsSL -o /tmp/hadolint "
            "https://github.com/hadolint/hadolint/releases/download/"
            f"v{HADOLINT_VERSION}/hadolint-linux-x86_64\n"
            f"printf '%s  %s\\n' {HADOLINT_LINUX_X86_64_SHA256}"
            " /tmp/hadolint | sha256sum --check --strict -\n"
            "sudo install -m 0755 /tmp/hadolint "
            "/usr/local/bin/hadolint\n"
            "hadolint --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_DOCKERFILE_LINT}"
        ),
    },
    {
        "name": JobStepName.PYTHON_FORMAT_CHECK,
        "run": f"{PROJEN_RUN} {TaskName.PYTHON_FORMAT_CHECK}",
    },
    {
        "name": JobStepName.GITHUB_ACTIONS_SCAN,
        "background": True,
        "run": (
            "curl -fsSL -o /tmp/zizmor.tar.gz "
            "https://github.com/zizmorcore/zizmor/releases/download/"
            f"v{ZIZMOR_VERSION}/"
            "zizmor-x86_64-unknown-linux-gnu.tar.gz\n"
            f"printf '%s  %s\\n' {ZIZMOR_LINUX_X64_TARBALL_SHA256}"
            " /tmp/zizmor.tar.gz | sha256sum --check --strict -\n"
            "tar -xzf /tmp/zizmor.tar.gz -C /tmp\n"
            "sudo install -m 0755 /tmp/zizmor /usr/local/bin/zizmor\n"
            "zizmor --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_GITHUB_ACTIONS_SCAN}"
        ),
    },
    {
        "name": JobStepName.IAC_SCAN,
        "background": True,
        "run": (
            f"{PROJEN_RUN} {TaskName.CDK_SYNTH_SILENT}\n"
            f"uvx --isolated checkov@{CHECKOV_VERSION} --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_IAC_SCAN}"
        ),
    },
    {"name": JobStepName.INSTALL_CDK_CLI, "run": "npm install -g aws-cdk@2.1146.1"},
    {"name": JobStepName.INSTALL_PYTHON_DEPENDENCIES, "run": "uv sync --frozen"},
    {"name": JobStepName.INSTALL_PROJEN_CLI, "run": "npm install -g projen@0.104.17"},
    {"name": JobStepName.PYTHON_LINT, "run": f"{PROJEN_RUN} {TaskName.PYTHON_LINT}"},
    {
        "name": JobStepName.MISCONFIG_SCAN,
        "background": True,
        "run": (
            "curl -fsSL -o /tmp/trivy.tar.gz "
            "https://github.com/aquasecurity/trivy/releases/download/"
            f"v{TRIVY_VERSION}/"
            f"trivy_{TRIVY_VERSION}_Linux-64bit.tar.gz\n"
            f"printf '%s  %s\\n' {TRIVY_LINUX_64BIT_TARBALL_SHA256}"
            " /tmp/trivy.tar.gz | sha256sum --check --strict -\n"
            "tar -xzf /tmp/trivy.tar.gz -C /tmp trivy\n"
            "sudo install -m 0755 /tmp/trivy /usr/local/bin/trivy\n"
            "trivy --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_MISCONFIG_SCAN}"
        ),
    },
    {"name": JobStepName.PYTHON_PACKAGE, "run": f"{PROJEN_RUN} {TaskName.PACKAGE}"},
    {
        "name": JobStepName.POST_CDK_DIFF,
        "env": {
            "GH_TOKEN": "${{ github.token }}",
            "PR_NUMBER": "${{ github.event.pull_request.number }}",
        },
        "run": POST_CDK_DIFF,
    },
    {
        "name": JobStepName.REGENERATE_PROJEN_FILES,
        "run": f"{PROJEN_RUN} --no-post --debug",
    },
    {
        "name": JobStepName.SAST_SCAN,
        "background": True,
        "run": (
            "curl -fsSL -o /tmp/opengrep "
            "https://github.com/opengrep/opengrep/releases/download/"
            f"v{OPENGREP_VERSION}/opengrep_manylinux_x86\n"
            f"printf '%s  %s\\n' {OPENGREP_MANYLINUX_X86_SHA256}"
            " /tmp/opengrep | sha256sum --check --strict -\n"
            "sudo install -m 0755 /tmp/opengrep /usr/local/bin/opengrep\n"
            "opengrep --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_SAST}"
        ),
    },
    {
        "name": JobStepName.SCA_MULTI_LANGUAGE,
        "background": True,
        "run": (
            "curl -fsSL -o /tmp/osv-scanner "
            "https://github.com/google/osv-scanner/releases/download/"
            f"v{OSV_SCANNER_VERSION}/osv-scanner_linux_amd64\n"
            f"printf '%s  %s\\n' {OSV_SCANNER_LINUX_AMD64_SHA256}"
            " /tmp/osv-scanner | sha256sum --check --strict -\n"
            "sudo install -m 0755 /tmp/osv-scanner "
            "/usr/local/bin/osv-scanner\n"
            "osv-scanner --version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_SCA_MULTI_LANGUAGE}"
        ),
    },
    {
        "name": JobStepName.SCA_PYTHON,
        "background": True,
        "run": f"{PROJEN_RUN} {TaskName.SECURITY_SCA_PYTHON}",
    },
    {
        "name": JobStepName.SECRET_SCAN,
        "background": True,
        "run": (
            'if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then\n'
            "  git fetch --unshallow\n"
            "fi\n"
            "curl -fsSL -o /tmp/gitleaks.tar.gz "
            "https://github.com/gitleaks/gitleaks/releases/download/"
            f"v{GITLEAKS_VERSION}/"
            f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz\n"
            f"printf '%s  %s\\n' {GITLEAKS_LINUX_X64_TARBALL_SHA256}"
            " /tmp/gitleaks.tar.gz | sha256sum --check --strict -\n"
            "tar -xzf /tmp/gitleaks.tar.gz -C /tmp\n"
            "sudo install -m 0755 /tmp/gitleaks /usr/local/bin/gitleaks\n"
            "gitleaks version\n"
            f"{PROJEN_RUN} {TaskName.SECURITY_SECRET_SCAN}"
        ),
    },
    {
        "name": JobStepName.INSTALL_NODE,
        "uses": SETUP_NODE_V4_PIN,
        "with_": {"node-version": NODE_VERSION},
    },
    {
        "name": JobStepName.INSTALL_UV,
        "uses": SETUP_UV_V5_PIN,
        "with_": {"python-version": PYTHON_VERSION},
    },
    {
        "name": JobStepName.PYTHON_STATIC_ANALYSIS,
        "run": f"{PROJEN_RUN} {TaskName.PYTHON_STATIC_ANALYSIS}",
    },
    {
        "name": JobStepName.PYTHON_TYPECHECK,
        "run": f"{PROJEN_RUN} {TaskName.PYTHON_TYPECHECK}",
    },
    {"name": JobStepName.PYTHON_UNIT_TESTS, "run": f"{PROJEN_RUN} {TaskName.TEST}"},
    {"name": JobStepName.WAIT_FOR_SCANS, "wait_all": True},
]

GITHUB_JOBS: Final[list[GitHubJobSpec]] = [
    {
        "id": JobName.CHECK,
        "runs_on": CI_RUNNERS,
        "permissions": {"contents": GitHubPermission.READ},
        "steps": [
            JobStepName.CHECKOUT,
            JobStepName.INSTALL_UV,
            JobStepName.INSTALL_NODE,
            JobStepName.INSTALL_PYTHON_DEPENDENCIES,
            JobStepName.INSTALL_PROJEN_CLI,
            JobStepName.REGENERATE_PROJEN_FILES,
            JobStepName.PYTHON_LINT,
            JobStepName.PYTHON_FORMAT_CHECK,
            JobStepName.PYTHON_TYPECHECK,
            JobStepName.PYTHON_STATIC_ANALYSIS,
            JobStepName.PYTHON_UNIT_TESTS,
            JobStepName.PYTHON_PACKAGE,
        ],
    },
    {
        "id": JobName.BUILD,
        "runs_on": CI_RUNNERS,
        "needs": [JobName.CHECK],
        "matrix": DEPLOYMENT_ENVIRONMENTS,
        "permissions": {
            "contents": GitHubPermission.READ,
            "id_token": GitHubPermission.WRITE,
            "pull_requests": GitHubPermission.WRITE,
        },
        "steps": [
            JobStepName.CHECKOUT,
            JobStepName.INSTALL_UV,
            JobStepName.INSTALL_NODE,
            JobStepName.INSTALL_CDK_CLI,
            JobStepName.INSTALL_PYTHON_DEPENDENCIES,
            JobStepName.INSTALL_PROJEN_CLI,
            JobStepName.AWS_CREDENTIALS,
            JobStepName.CDK_SYNTH,
            JobStepName.CDK_DIFF_CAPTURE,
            JobStepName.POST_CDK_DIFF,
        ],
    },
    {
        "id": JobName.DEPLOY,
        "runs_on": CI_RUNNERS,
        "needs": [JobName.CHECK],
        "matrix": DEPLOYMENT_ENVIRONMENTS,
        "permissions": {
            "contents": GitHubPermission.READ,
            "id_token": GitHubPermission.WRITE,
        },
        "steps": [
            JobStepName.CHECKOUT,
            JobStepName.INSTALL_UV,
            JobStepName.INSTALL_NODE,
            JobStepName.INSTALL_CDK_CLI,
            JobStepName.INSTALL_PYTHON_DEPENDENCIES,
            JobStepName.INSTALL_PROJEN_CLI,
            JobStepName.AWS_CREDENTIALS,
            JobStepName.CDK_DIFF,
            JobStepName.CDK_DEPLOY,
        ],
    },
    {
        "id": JobName.SCAN,
        "runs_on": CI_RUNNERS,
        "permissions": {"contents": GitHubPermission.READ},
        "steps": [
            JobStepName.CHECKOUT,
            JobStepName.INSTALL_UV,
            JobStepName.INSTALL_NODE,
            JobStepName.INSTALL_CDK_CLI,
            JobStepName.INSTALL_PYTHON_DEPENDENCIES,
            JobStepName.INSTALL_PROJEN_CLI,
            JobStepName.SECRET_SCAN,
            JobStepName.SAST_SCAN,
            JobStepName.MISCONFIG_SCAN,
            JobStepName.SCA_PYTHON,
            JobStepName.IAC_SCAN,
            JobStepName.GITHUB_ACTIONS_SCAN,
            JobStepName.SCA_MULTI_LANGUAGE,
            JobStepName.DOCKERFILE_SCAN,
            JobStepName.WAIT_FOR_SCANS,
        ],
    },
]

GITHUB_WORKFLOWS: Final[list[GitHubWorkflowSpec]] = [
    {
        "name": WorkflowName.BUILD,
        "on": {"pull_request": {}},
        "jobs": [JobName.CHECK, JobName.BUILD],
    },
    {
        "name": WorkflowName.DEPLOY,
        "on": {"push": {"branches": ["main"]}, "workflow_dispatch": {}},
        "jobs": [JobName.CHECK, JobName.DEPLOY],
    },
    {
        "name": WorkflowName.SECURITY,
        "on": {"pull_request": {}, "workflow_dispatch": {}},
        "jobs": [JobName.SCAN],
    },
]
