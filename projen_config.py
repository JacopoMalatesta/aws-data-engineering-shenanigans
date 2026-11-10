"""Project configuration data consumed by ``.projenrc.py`` and ``app.py``.

This module stores configuration only. It never creates projen resources.
"""

from typing import Final, cast

from aws_cdk.region_info import RegionInfo

from constants import (
    ACTIONLINT_LINUX_AMD64_TARBALL_SHA256,
    ACTIONLINT_VERSION,
    AIRFLOW_RUFF_RULESET,
    AWS_CREDENTIALS_V6_PIN,
    CHECKOUT_V7_PIN,
    CHECKOV_VERSION,
    COMMITLINT_CLI_VERSION,
    COMMITLINT_CONFIG_CONVENTIONAL_VERSION,
    COMMITLINT_RULE_CONDITION_ALWAYS,
    COMMITLINT_RULE_SEVERITY_ERROR,
    DEPTRY_RULE_MISPLACED_DEV_DEPENDENCY,
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
    PRE_COMMIT_LANGUAGE_NODE,
    PRE_COMMIT_LANGUAGE_UNSUPPORTED,
    PRE_COMMIT_LANGUAGE_VERSION_SYSTEM,
    PROJEN_RUN,
    PYTHON_VERSION,
    SETUP_NODE_V7_PIN,
    SETUP_UV_V10_PIN,
    TRIVY_LINUX_64BIT_TARBALL_SHA256,
    TRIVY_VERSION,
    VIRTUAL_ENV_BINARY_DIR,
    YAMLLINT_VERSION,
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
    ProjectSpec,
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
    "deptry@0.25.1",
    "pre-commit@4.6.2",
    "pytest-cov@7.1.0",
    "ruff@0.17.2",
    "ty@0.0.92",
]


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

PYPROJECT_TOOL_SECTIONS: Final = {
    "ruff": {
        "target-version": f"py{PYTHON_VERSION.replace('.', '')}",
        "line-length": 88,
        "lint": {
            "preview": True,
            "select": ["ALL"],
            "ignore": RUFF_IGNORE_RULES,
            "pydocstyle": {"convention": "google"},
            "per-file-ignores": RUFF_PER_FILE_IGNORES,
        },
    },
    "ty": {
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
    "basedpyright": {
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
    # DEP004: projen is generator-injected and imported only by dev-only scripts.
    "deptry": {
        "per_rule_ignores": {DEPTRY_RULE_MISPLACED_DEV_DEPENDENCY: ["projen"]},
    },
    "pytest.ini_options": {
        "addopts": (
            "-vv -ra --durations=10 "
            f"--cov={PROJECT_SPEC['module_name']} "
            "--cov-report=term-missing"
        ),
        "testpaths": ["tests"],
    },
}

PROJEN_TASKS: Final[dict[TaskName, ProjenTaskSpec]] = {
    TaskName.PYTHON_LINT: {
        "description": "Lint with ruff",
        "exec": "ruff check .",
    },
    TaskName.PYTHON_LINT_FIX: {
        "description": "Autofix ruff violations (safe fixes only)",
        "exec": "ruff check --fix .",
    },
    TaskName.PYTHON_FORMAT: {
        "description": "Format code with ruff",
        "exec": "ruff format .",
    },
    TaskName.PYTHON_FORMAT_CHECK: {
        "description": "Verify ruff formatting",
        "exec": "ruff format --check .",
    },
    TaskName.PYTHON_STATIC_ANALYSIS: {
        "description": "Static analysis with basedpyright",
        "exec": "basedpyright",
    },
    TaskName.PYTHON_DEPENDENCY_LINT: {
        "description": "Check declared dependencies against imported modules with deptry",
        "exec": "deptry .",
    },
    TaskName.PYTHON_TYPECHECK: {
        "description": "Type check with ty",
        "exec": "ty check --error-on-warning .",
    },
    TaskName.PYTHON_CHECK: {
        "description": "Run all static checks: lint, format check, type check",
        "spawns": [
            TaskName.PYTHON_LINT,
            TaskName.PYTHON_FORMAT_CHECK,
            TaskName.PYTHON_TYPECHECK,
            TaskName.PYTHON_STATIC_ANALYSIS,
            TaskName.PYTHON_DEPENDENCY_LINT,
        ],
    },
    TaskName.CDK_SYNTH: {
        "description": (
            "Synthesize the CDK app into cdk.out, failing on warnings "
            "(--strict), so IaC policy warnings gate CI alongside errors"
        ),
        "exec": "cdk synth --strict",
    },
    TaskName.SECURITY_SCA_PYTHON: {
        "description": "Audit uv.lock for known vulnerabilities and deprecated projects",
        "exec": "uv audit --preview-features audit-command",
    },
    TaskName.SECURITY_SAST: {
        "description": "Static pattern scan of tracked sources (three rulesets)",
        "exec": (
            "opengrep scan --verbose --config p/security-audit --config p/owasp-top-ten"
            " --config p/python ."
        ),
    },
    TaskName.SECURITY_SECRET_SCAN: {
        "description": "Scan the full git history for leaked credentials",
        "exec": "gitleaks detect --no-banner --config .gitleaks.toml",
    },
    TaskName.SECURITY_MISCONFIG_SCAN: {
        "description": "Misconfiguration scan of the workspace (Dockerfile etc.)",
        "exec": "trivy fs --config trivy.yaml --exit-code 1 .",
    },
    TaskName.SECURITY_IAC_SCAN: {
        "description": "IaC policy scan of the synthesized CloudFormation template (cdk.out)",
        "exec": f"uvx --isolated checkov@{CHECKOV_VERSION} --config-file .checkov.yaml --show-config",
    },
    TaskName.SECURITY_GITHUB_ACTIONS_SCAN: {
        "description": "Static analysis of GitHub Actions workflows",
        "exec": "zizmor .",
    },
    TaskName.GITHUB_ACTIONS_LINT: {
        "description": "Lint GitHub Actions workflows with actionlint",
        "exec": "actionlint",
    },
    TaskName.SECURITY_SCA_MULTI_LANGUAGE: {
        "description": "Scan dependencies for known vulnerabilities (OSV)",
        "exec": "osv-scanner scan source --recursive .",
    },
    TaskName.SECURITY_DOCKERFILE_LINT: {
        "description": "Lint Dockerfiles with Hadolint",
        "exec": (
            "find . -name 'Dockerfile*' -not -path './.venv/*' "
            "-not -path '*/node_modules/*' -exec hadolint {} +"
        ),
    },
    # PyPI-only tool: uvx (isolated) instead of the curl/sha256 binary pattern.
    TaskName.YAML_LINT: {
        "description": "Lint YAML files with yamllint",
        "exec": f"uvx --isolated yamllint@{YAMLLINT_VERSION} .",
    },
    TaskName.SECURITY: {
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
}

COMMITLINT_NPM_PACKAGES: Final = [
    f"@commitlint/cli@{COMMITLINT_CLI_VERSION}",
    f"@commitlint/config-conventional@{COMMITLINT_CONFIG_CONVENTIONAL_VERSION}",
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
    {
        "id": "deptry-check",
        "name": "deptry",
        "entry": f"{VIRTUAL_ENV_BINARY_DIR}deptry",
        "args": ["."],
        "language": PRE_COMMIT_LANGUAGE_UNSUPPORTED,
        "pass_filenames": False,
        "files": r"\.py$|pyproject\.toml$",
    },
    {
        "id": "commitlint",
        "name": "commitlint",
        "entry": "commitlint",
        "args": ["--edit"],
        "language": PRE_COMMIT_LANGUAGE_NODE,
        "language_version": PRE_COMMIT_LANGUAGE_VERSION_SYSTEM,
        "additional_dependencies": COMMITLINT_NPM_PACKAGES,
        "stages": ["commit-msg"],
    },
]

PROJECT_FILES: Final[dict[str, FileSpec]] = {
    ".pre-commit-config.yaml": {
        "file_type": FileType.YAML,
        "obj": {
            # pre-commit runs hooks in every stage by default — keep the
            # code checks at pre-commit; commitlint opts into commit-msg.
            "default_stages": ["pre-commit"],
            "repos": [
                {
                    "repo": "local",
                    "hooks": cast("list[JsonValue]", PRE_COMMIT_HOOKS),
                }
            ],
        },
    },
    ".commitlintrc.yaml": {
        "file_type": FileType.YAML,
        "obj": {
            "extends": ["@commitlint/config-conventional"],
            "rules": {
                "type-enum": [
                    COMMITLINT_RULE_SEVERITY_ERROR,
                    COMMITLINT_RULE_CONDITION_ALWAYS,
                    [*SEMANTIC_TITLE_TYPES],
                ],
            },
        },
    },
    "trivy.yaml": {
        "file_type": FileType.YAML,
        "obj": {
            "severity": ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "scan": {
                "scanners": ["misconfig"],
                "skip-dirs": [".venv", "cdk.out", "node_modules", ".git"],
            },
        },
    },
    ".gitleaks.toml": {
        "file_type": FileType.TOML,
        "obj": {
            "title": "aws-data-engineering-shenanigans gitleaks policy",
            "extend": {"useDefault": True},
        },
    },
    "zizmor.yml": {
        "file_type": FileType.YAML,
        "obj": {
            "rules": {
                "adhoc-packages": {
                    "ignore": [
                        "build.yml",
                        "commitlint.yml",
                        "deploy.yml",
                        "security.yml",
                    ]
                },
                "dangerous-triggers": {"ignore": ["pull-request-lint.yml"]},
            }
        },
    },
    # rhysd/actionlint#693: parallel-step keys ("background", "wait-all")
    # are unrecognized by actionlint v1.7.12; the run/uses error is the
    # derived "wait-all" finding. Scope both to the scan job and drop
    # this entry once #694 ships.
    ".github/actionlint.yaml": {
        "file_type": FileType.YAML,
        "obj": {
            "paths": {
                ".github/workflows/security.yml": {
                    "ignore": [
                        'unexpected key "background"',
                        'step must run script with "run" section or run action with "uses" section',
                    ],
                },
            },
        },
    },
    ".hadolint.yaml": {
        "file_type": FileType.YAML,
        "obj": {},
    },
    ".yamllint.yaml": {
        "file_type": FileType.YAML,
        "obj": {
            "extends": "default",
            # yamllint ignores .gitignore: skip vendored/generated trees.
            "ignore": (
                ".venv/\n"
                "node_modules/\n"
                "cdk.out/\n"
                ".projen/\n"
                "dist/\n"
                ".pytest_cache/\n"
                ".ruff_cache/\n"
                ".opencode/\n"
                ".git/"
            ),
            "rules": {
                # GH Actions 'on:' key trips the truthy check.
                "truthy": {"check-keys": False},
                # Projen never emits a leading '---'.
                "document-start": "disable",
                "line-length": {"max": 160},
            },
        },
    },
    "osv-scanner.toml": {
        "file_type": FileType.TOML,
        "obj": {},
    },
    ".checkov.yaml": {
        "file_type": FileType.YAML,
        "obj": {"framework": ["cloudformation"], "directory": "cdk.out"},
    },
    ".github/dependabot.yml": {
        "file_type": FileType.YAML,
        "obj": {
            "version": 2,
            "updates": [
                {
                    "package-ecosystem": "github-actions",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "cooldown": {"default-days": 7},
                    "groups": {"actions": {"patterns": ["*"]}},
                    "open-pull-requests-limit": 5,
                    "commit-message": {"prefix": "chore(deps)", "include": "scope"},
                },
                {
                    "package-ecosystem": "uv",
                    "directory": "/",
                    "schedule": {"interval": "weekly"},
                    "cooldown": {"default-days": 7},
                    "groups": {"python": {"patterns": ["*"]}},
                    "open-pull-requests-limit": 5,
                    "commit-message": {"prefix": "chore(deps)", "include": "scope"},
                },
            ],
        },
    },
}

DEPLOYMENT_ENVIRONMENTS: Final[list[DeploymentEnvironment]] = [
    {
        "environment_name": EnvironmentName.DEV,
        "aws_account_id": "925000840053",
        "region_name": RegionInfo.get("eu-west-1").name,
    },
]

CI_RUNNERS: Final = ["ubuntu-latest"]

# Steps referenced by more than one job, hoisted for single-sourcing;
# single-use steps are declared inline in the prelude or in their job's
# ``steps`` mapping.
AWS_CREDENTIALS_STEP: Final[GitHubJobStepSpec] = {
    "uses": AWS_CREDENTIALS_V6_PIN,
    "with_": {
        "role-to-assume": "arn:aws:iam::${{ matrix.aws_account_id }}:role/github-actions-deploy",
        "aws-region": "${{ matrix.region_name }}",
    },
}
INSTALL_NODE_STEP: Final[GitHubJobStepSpec] = {
    "uses": SETUP_NODE_V7_PIN,
    "with_": {"node-version": NODE_VERSION},
}

# Setup shared by several jobs
_SETUP: Final[dict[JobStepName, GitHubJobStepSpec]] = {
    JobStepName.CHECKOUT: {
        "uses": CHECKOUT_V7_PIN,
        "with_": {"persist-credentials": False},
    },
    JobStepName.INSTALL_UV: {
        "uses": SETUP_UV_V10_PIN,
        "with_": {"python-version": PYTHON_VERSION},
    },
    JobStepName.INSTALL_NODE: INSTALL_NODE_STEP,
    JobStepName.INSTALL_PYTHON_DEPENDENCIES: {"run": "uv sync --frozen"},
    JobStepName.INSTALL_PROJEN_CLI: {"run": "npm install -g projen@0.104.17"},
}
_SETUP_CDK: Final[dict[JobStepName, GitHubJobStepSpec]] = {
    **_SETUP,
    JobStepName.INSTALL_CDK_CLI: {"run": "npm install -g aws-cdk@2.1146.1"},
}

# The check job gates both the build and deploy workflows, so it is
# declared once here instead of per workflow.
CHECK_JOB: Final[GitHubJobSpec] = {
    "runs_on": CI_RUNNERS,
    "permissions": {"contents": GitHubPermission.READ},
    "steps": {
        **_SETUP,
        JobStepName.REGENERATE_PROJEN_FILES: {
            "run": f"{PROJEN_RUN} --no-post --debug",
        },
        JobStepName.REGEN_DRIFT_CHECK: {"run": "git diff --exit-code"},
        JobStepName.YAML_LINT: {
            "run": (
                f"uvx --isolated yamllint@{YAMLLINT_VERSION} --version\n"
                f"{PROJEN_RUN} {TaskName.YAML_LINT}"
            ),
        },
        JobStepName.GITHUB_ACTIONS_LINT: {
            "run": (
                "curl -fsSL -o /tmp/actionlint.tar.gz "
                "https://github.com/rhysd/actionlint/releases/"
                "download/"
                f"v{ACTIONLINT_VERSION}/"
                f"actionlint_{ACTIONLINT_VERSION}_linux_amd64.tar.gz\n"
                f"printf '%s  %s\\n' "
                f"{ACTIONLINT_LINUX_AMD64_TARBALL_SHA256}"
                " /tmp/actionlint.tar.gz | sha256sum --check"
                " --strict -\n"
                "tar -xzf /tmp/actionlint.tar.gz -C /tmp\n"
                "sudo install -m 0755 /tmp/actionlint "
                "/usr/local/bin/actionlint\n"
                "actionlint --version\n"
                f"{PROJEN_RUN} {TaskName.GITHUB_ACTIONS_LINT}"
            ),
        },
        JobStepName.PYTHON_LINT: {
            "run": f"{PROJEN_RUN} {TaskName.PYTHON_LINT}",
        },
        JobStepName.PYTHON_FORMAT_CHECK: {
            "run": f"{PROJEN_RUN} {TaskName.PYTHON_FORMAT_CHECK}",
        },
        JobStepName.PYTHON_TYPECHECK: {
            "run": f"{PROJEN_RUN} {TaskName.PYTHON_TYPECHECK}",
        },
        JobStepName.PYTHON_STATIC_ANALYSIS: {
            "run": f"{PROJEN_RUN} {TaskName.PYTHON_STATIC_ANALYSIS}",
        },
        JobStepName.PYTHON_DEPENDENCY_LINT: {
            "run": f"{PROJEN_RUN} {TaskName.PYTHON_DEPENDENCY_LINT}",
        },
        JobStepName.PYTHON_UNIT_TESTS: {"run": f"{PROJEN_RUN} {TaskName.TEST}"},
        JobStepName.PYTHON_PACKAGE: {
            "run": f"{PROJEN_RUN} {TaskName.PACKAGE}",
        },
    },
}

GITHUB_WORKFLOWS: Final[dict[WorkflowName, GitHubWorkflowSpec]] = {
    WorkflowName.BUILD: {
        "on": {"pull_request": {}},
        "jobs": {
            JobName.CHECK: CHECK_JOB,
            JobName.BUILD: {
                "runs_on": CI_RUNNERS,
                "needs": [JobName.CHECK],
                "matrix": DEPLOYMENT_ENVIRONMENTS,
                "max_parallel": 1,
                "fail_fast": True,
                "permissions": {
                    "contents": GitHubPermission.READ,
                    "id_token": GitHubPermission.WRITE,
                    "pull_requests": GitHubPermission.WRITE,
                },
                "steps": {
                    **_SETUP_CDK,
                    JobStepName.AWS_CREDENTIALS: AWS_CREDENTIALS_STEP,
                    JobStepName.CDK_SYNTH: {
                        "run": f"{PROJEN_RUN} {TaskName.CDK_SYNTH}",
                    },
                    JobStepName.CDK_DIFF_CAPTURE: {
                        "run": f"{PROJEN_RUN} {TaskName.CDK_DIFF} > cdk-diff.txt || true",
                    },
                    JobStepName.POST_CDK_DIFF: {
                        "env": {
                            "GH_TOKEN": "${{ github.token }}",
                            "PR_NUMBER": "${{ github.event.pull_request.number }}",
                        },
                        "run": POST_CDK_DIFF,
                    },
                },
            },
        },
    },
    WorkflowName.COMMIT_LINT: {
        "on": {"pull_request": {}},
        "jobs": {
            JobName.COMMIT_LINT: {
                "runs_on": CI_RUNNERS,
                "permissions": {"contents": GitHubPermission.READ},
                "steps": {
                    JobStepName.CHECKOUT_FULL_HISTORY: {
                        "uses": CHECKOUT_V7_PIN,
                        "with_": {
                            "persist-credentials": False,
                            "fetch-depth": 0,
                        },
                    },
                    JobStepName.INSTALL_NODE: INSTALL_NODE_STEP,
                    JobStepName.COMMIT_LINT: {
                        "run": (
                            "npm install --no-save --no-package-lock "
                            f"{COMMITLINT_NPM_PACKAGES[0]} "
                            f"{COMMITLINT_NPM_PACKAGES[1]}\n"
                            "npx --no-install commitlint --version\n"
                            "npx --no-install commitlint --from="
                            "${{ github.event.pull_request.base.sha }} "
                            "--to=${{ github.event.pull_request.head.sha }}"
                            " --verbose"
                        ),
                    },
                },
            },
        },
    },
    WorkflowName.DEPLOY: {
        "on": {"push": {"branches": ["main"]}, "workflow_dispatch": {}},
        "limit_concurrency": True,
        "jobs": {
            JobName.CHECK: CHECK_JOB,
            JobName.DEPLOY: {
                "runs_on": CI_RUNNERS,
                "needs": [JobName.CHECK],
                "matrix": DEPLOYMENT_ENVIRONMENTS,
                "max_parallel": 1,
                "fail_fast": True,
                "permissions": {
                    "contents": GitHubPermission.READ,
                    "id_token": GitHubPermission.WRITE,
                },
                "steps": {
                    **_SETUP_CDK,
                    JobStepName.AWS_CREDENTIALS: AWS_CREDENTIALS_STEP,
                    JobStepName.CDK_DIFF: {
                        "run": f"{PROJEN_RUN} {TaskName.CDK_DIFF}",
                    },
                    JobStepName.CDK_DEPLOY: {
                        "run": (
                            f"{PROJEN_RUN} deploy "
                            f'"*-${{{{ matrix.environment_name }}}}"'
                        ),
                    },
                },
            },
        },
    },
    WorkflowName.SECURITY: {
        "on": {"pull_request": {}, "workflow_dispatch": {}},
        "jobs": {
            JobName.SCAN: {
                "runs_on": CI_RUNNERS,
                "permissions": {"contents": GitHubPermission.READ},
                "steps": {
                    **_SETUP_CDK,
                    JobStepName.SECRET_SCAN: {
                        "background": True,
                        "run": (
                            'if [ "$(git rev-parse --is-shallow-repository)"'
                            ' = "true" ]; then\n'
                            "  git fetch --unshallow\n"
                            "fi\n"
                            "curl -fsSL -o /tmp/gitleaks.tar.gz "
                            "https://github.com/gitleaks/gitleaks/releases/"
                            "download/"
                            f"v{GITLEAKS_VERSION}/"
                            f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz\n"
                            f"printf '%s  %s\\n' {GITLEAKS_LINUX_X64_TARBALL_SHA256}"
                            " /tmp/gitleaks.tar.gz | sha256sum --check --strict -\n"
                            "tar -xzf /tmp/gitleaks.tar.gz -C /tmp\n"
                            "sudo install -m 0755 /tmp/gitleaks /usr/local/bin"
                            "/gitleaks\n"
                            "gitleaks version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_SECRET_SCAN}"
                        ),
                    },
                    JobStepName.SAST_SCAN: {
                        "background": True,
                        "run": (
                            "curl -fsSL -o /tmp/opengrep "
                            "https://github.com/opengrep/opengrep/releases/"
                            "download/"
                            f"v{OPENGREP_VERSION}/opengrep_manylinux_x86\n"
                            f"printf '%s  %s\\n' {OPENGREP_MANYLINUX_X86_SHA256}"
                            " /tmp/opengrep | sha256sum --check --strict -\n"
                            "sudo install -m 0755 /tmp/opengrep "
                            "/usr/local/bin/opengrep\n"
                            "opengrep --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_SAST}"
                        ),
                    },
                    JobStepName.MISCONFIG_SCAN: {
                        "background": True,
                        "run": (
                            "curl -fsSL -o /tmp/trivy.tar.gz "
                            "https://github.com/aquasecurity/trivy/releases/"
                            "download/"
                            f"v{TRIVY_VERSION}/"
                            f"trivy_{TRIVY_VERSION}_Linux-64bit.tar.gz\n"
                            f"printf '%s  %s\\n' {TRIVY_LINUX_64BIT_TARBALL_SHA256}"
                            " /tmp/trivy.tar.gz | sha256sum --check --strict -\n"
                            "tar -xzf /tmp/trivy.tar.gz -C /tmp trivy\n"
                            "sudo install -m 0755 /tmp/trivy /usr/local/bin"
                            "/trivy\n"
                            "trivy --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_MISCONFIG_SCAN}"
                        ),
                    },
                    JobStepName.SCA_PYTHON: {
                        "background": True,
                        "run": f"{PROJEN_RUN} {TaskName.SECURITY_SCA_PYTHON}",
                    },
                    JobStepName.IAC_SCAN: {
                        "background": True,
                        "run": (
                            f"{PROJEN_RUN} {TaskName.CDK_SYNTH_SILENT}\n"
                            f"uvx --isolated checkov@{CHECKOV_VERSION} --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_IAC_SCAN}"
                        ),
                    },
                    JobStepName.GITHUB_ACTIONS_SCAN: {
                        "background": True,
                        "run": (
                            "curl -fsSL -o /tmp/zizmor.tar.gz "
                            "https://github.com/zizmorcore/zizmor/releases/"
                            "download/"
                            f"v{ZIZMOR_VERSION}/"
                            "zizmor-x86_64-unknown-linux-gnu.tar.gz\n"
                            f"printf '%s  %s\\n' {ZIZMOR_LINUX_X64_TARBALL_SHA256}"
                            " /tmp/zizmor.tar.gz | sha256sum --check --strict -\n"
                            "tar -xzf /tmp/zizmor.tar.gz -C /tmp\n"
                            "sudo install -m 0755 /tmp/zizmor /usr/local/bin"
                            "/zizmor\n"
                            "zizmor --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_GITHUB_ACTIONS_SCAN}"
                        ),
                    },
                    JobStepName.SCA_MULTI_LANGUAGE: {
                        "background": True,
                        "run": (
                            "curl -fsSL -o /tmp/osv-scanner "
                            "https://github.com/google/osv-scanner/releases/"
                            "download/"
                            f"v{OSV_SCANNER_VERSION}/osv-scanner_linux_amd64\n"
                            f"printf '%s  %s\\n' {OSV_SCANNER_LINUX_AMD64_SHA256}"
                            " /tmp/osv-scanner | sha256sum --check --strict -\n"
                            "sudo install -m 0755 /tmp/osv-scanner "
                            "/usr/local/bin/osv-scanner\n"
                            "osv-scanner --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_SCA_MULTI_LANGUAGE}"
                        ),
                    },
                    JobStepName.DOCKERFILE_SCAN: {
                        "background": True,
                        "run": (
                            "curl -fsSL -o /tmp/hadolint "
                            "https://github.com/hadolint/hadolint/releases/"
                            "download/"
                            f"v{HADOLINT_VERSION}/hadolint-linux-x86_64\n"
                            f"printf '%s  %s\\n' {HADOLINT_LINUX_X86_64_SHA256}"
                            " /tmp/hadolint | sha256sum --check --strict -\n"
                            "sudo install -m 0755 /tmp/hadolint "
                            "/usr/local/bin/hadolint\n"
                            "hadolint --version\n"
                            f"{PROJEN_RUN} {TaskName.SECURITY_DOCKERFILE_LINT}"
                        ),
                    },
                    JobStepName.WAIT_FOR_SCANS: {"wait_all": True},
                },
            },
        },
    },
}
