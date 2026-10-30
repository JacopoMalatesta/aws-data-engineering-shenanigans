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
CI_RUNNER: Final = "ubuntu-latest"
NODE_VERSION: Final = "24"
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
# Tool configuration is projen-managed in ruff.toml and ty.toml below.
# ------------------------------------------------------------------
# Ruff configuration - projen-managed. Reference:
# https://docs.astral.sh/ruff/configuration/
TomlFile(
    project,
    "ruff.toml",
    obj={
        "target-version": f"py{PYTHON_VERSION.replace('.', '')}",
        "line-length": 88,
        "lint": {
            "preview": True,
            "select": ["ALL"],
            "ignore": [
                # Rules that conflict with the ruff formatter:
                # https://docs.astral.sh/ruff/formatter/#conflicting-lint-rules
                "tab-indentation",  # W191
                "indentation-with-invalid-multiple",  # E111
                "indentation-with-invalid-multiple-comment",  # E114
                "over-indented",  # E117
                "incorrect-blank-line-before-class",  # D203 (D211 preferred)
                "docstring-tab-indentation",  # D206
                "triple-single-quotes",  # D300
                "bad-quotes-inline-string",  # Q000
                "bad-quotes-multiline-string",  # Q001
                "bad-quotes-docstring",  # Q002
                "avoidable-escaped-quote",  # Q003
                "missing-trailing-comma",  # COM812
                "prohibited-trailing-comma",  # COM819
                "multi-line-implicit-string-concatenation",  # ISC002
                # The formatter governs wrapping (best-effort only), so the
                # linter must not fight it over line length.
                "line-too-long",  # E501
                # Framework-specific rule families for libraries this repo
                # doesn't use.
                "AIR",  # airflow
                "DJ",  # django
                "FAST",  # fastapi
                "NPY",  # numpy
                "PD",  # pandas
                # Noisy preview rules observed with select=ALL; re-evaluate
                # on upgrades.
                "missing-copyright-notice",  # CPY001
            ],
            "pydocstyle": {"convention": "google"},
            "per-file-ignores": {
                "tests/**": [
                    "assert",
                    "undocumented-public-module",
                    "undocumented-public-class",
                    "undocumented-public-method",
                    "undocumented-public-function",
                    "undocumented-public-package",
                ],
                "**/__init__.py": ["undocumented-public-package"],
            },
        },
    },
)
# ty configuration - projen-managed. Astral's documented "even stricter"
# recipe (https://docs.astral.sh/ty/coming-from-mypy-or-pyright/): stricter
# than mypy/pyright --strict. The known-false-positive trio
# (division-by-zero, possibly-missing-attribute, possibly-missing-import)
# is deliberately NOT enabled.
TomlFile(
    project,
    "ty.toml",
    obj={
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
)
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
    "zizmor.yml",
    obj={
        "rules": {
            "adhoc-packages": {"ignore": ["build.yml", "deploy.yml", "security.yml"]},
            "dangerous-triggers": {"ignore": ["pull-request-lint.yml"]},
        }
    },
)
YamlFile(
    project,
    ".hadolint.yaml",
    obj={},
)
TomlFile(
    project,
    "osv-scanner.toml",
    obj={},
)
YamlFile(
    project,
    ".checkov.yaml",
    obj={"framework": ["cloudformation"], "directory": "cdk.out"},
)

security_sca_python = project.add_task(
    "security:sca-python",
    description="Audit uv.lock for known vulnerabilities and deprecated projects",
    exec="uv audit --preview-features audit-command",
)
security_sast = project.add_task(
    "security:sast",
    description="Static pattern scan of tracked sources (three rulesets)",
    exec=(
        "opengrep scan --verbose --config p/security-audit --config p/owasp-top-ten"
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
    exec=f"uvx --isolated checkov@{CHECKOV_VERSION} --config-file .checkov.yaml --show-config",
)

security_git_hub_actions_scan = project.add_task(
    "security:git-hub-actions-scan",
    description="Static analysis of GitHub Actions workflows",
    exec="zizmor .",
)
security_sca_multi = project.add_task(
    "security:sca-multi",
    description="Scan dependencies for known vulnerabilities (OSV)",
    exec="osv-scanner scan source --recursive .",
)
security_dockerfile_lint = project.add_task(
    "security:dockerfile-lint",
    description="Lint Dockerfiles with Hadolint",
    exec=(
        "find . -name 'Dockerfile*' -not -path './.venv/*' "
        "-not -path '*/node_modules/*' -exec hadolint {} +"
    ),
)

security = project.add_task(
    "security",
    description=(
        "Run all security scanners: dependency audit, secret history, "
        "source patterns, config misconfigurations, IaC policy"
    ),
)
security.spawn(security_sca_python)
security.spawn(security_sast)
security.spawn(security_secret_scan)
security.spawn(security_misconfig_scan)
security.spawn(security_iac_scan)
security.spawn(security_git_hub_actions_scan)
security.spawn(security_sca_multi)
security.spawn(security_dockerfile_lint)

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
    JobStep(uses=CHECKOUT_V4_PIN, with_={"persist-credentials": False}),
    JobStep(uses=SETUP_UV_V5_PIN, with_={"python-version": PYTHON_VERSION}),
    JobStep(uses=SETUP_NODE_V4_PIN, with_={"node-version": NODE_VERSION}),
    JobStep(name="Install CDK CLI", run="npm install -g aws-cdk@2.1146.1"),
    JobStep(name="Install dependencies", run="uv sync --frozen"),
    JobStep(name="Install projen CLI", run="npm install -g projen@0.104.17"),
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
gh pr comment "$PR_NUMBER" --edit-last --create-if-none --body-file "$DIFF_BODY_FILE"
"""

# ------------------------------------------------------------------
# GitHub Actions: build + synth + tests on every pull request
# ------------------------------------------------------------------
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
                    "PR_NUMBER": "${{ github.event.pull_request.number }}",
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
        runs_on=[CI_RUNNER],
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

security = github.add_workflow("security")
security.on(pull_request={}, workflow_dispatch={})

security.add_job(
    "scan",
    Job(
        runs_on=[CI_RUNNER],
        permissions={"contents": JobPermission.READ},
        steps=[
            *SETUP_STEPS,
            JobStep(
                name="Secret scan",
                background=True,
                run=(
                    'if [ "$(git rev-parse --is-shallow-repository)" = "true" ]; then\n'
                    "  git fetch --unshallow\n"
                    "fi\n"
                    "curl -fsSL -o /tmp/gitleaks.tar.gz "
                    f"https://github.com/gitleaks/gitleaks/releases/download/"
                    f"v{GITLEAKS_VERSION}/"
                    f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz\n"
                    f"printf '%s  %s\\n' {GITLEAKS_LINUX_X64_TARBALL_SHA256}"
                    " /tmp/gitleaks.tar.gz | sha256sum --check --strict -\n"
                    "tar -xzf /tmp/gitleaks.tar.gz -C /tmp\n"
                    "sudo install -m 0755 /tmp/gitleaks /usr/local/bin/gitleaks\n"
                    "gitleaks version\n"
                    f"{PROJEN_RUN} {security_secret_scan.name}"
                ),
            ),
            JobStep(
                name="SAST scan",
                background=True,
                run=(
                    "curl -fsSL -o /tmp/opengrep "
                    "https://github.com/opengrep/opengrep/releases/download/"
                    f"v{OPENGREP_VERSION}/opengrep_manylinux_x86\n"
                    f"printf '%s  %s\\n' {OPENGREP_MANYLINUX_X86_SHA256}"
                    " /tmp/opengrep | sha256sum --check --strict -\n"
                    "sudo install -m 0755 /tmp/opengrep /usr/local/bin/opengrep\n"
                    "opengrep --version\n"
                    f"{PROJEN_RUN} {security_sast.name}"
                ),
            ),
            JobStep(
                name="Misconfig scan",
                background=True,
                run=(
                    "curl -fsSL -o /tmp/trivy.tar.gz "
                    "https://github.com/aquasecurity/trivy/releases/download/"
                    f"v{TRIVY_VERSION}/"
                    f"trivy_{TRIVY_VERSION}_Linux-64bit.tar.gz\n"
                    f"printf '%s  %s\\n' {TRIVY_LINUX_64BIT_TARBALL_SHA256}"
                    " /tmp/trivy.tar.gz | sha256sum --check --strict -\n"
                    "tar -xzf /tmp/trivy.tar.gz -C /tmp trivy\n"
                    "sudo install -m 0755 /tmp/trivy /usr/local/bin/trivy\n"
                    "trivy --version\n"
                    f"{PROJEN_RUN} {security_misconfig_scan.name}"
                ),
            ),
            JobStep(
                name="SCA (Python)",
                background=True,
                run=f"{PROJEN_RUN} {security_sca_python.name}",
            ),
            JobStep(
                name="IaC scan",
                background=True,
                run=(
                    f"{PROJEN_RUN} {_get_task_by_name('synth:silent').name}\n"
                    f"uvx --isolated checkov@{CHECKOV_VERSION} --version\n"
                    f"{PROJEN_RUN} {security_iac_scan.name}"
                ),
            ),
            JobStep(
                name="GitHub Actions scan",
                background=True,
                run=(
                    "curl -fsSL -o /tmp/zizmor.tar.gz "
                    "https://github.com/zizmorcore/zizmor/releases/download/"
                    f"v{ZIZMOR_VERSION}/"
                    "zizmor-x86_64-unknown-linux-gnu.tar.gz\n"
                    f"printf '%s  %s\\n' {ZIZMOR_LINUX_X64_TARBALL_SHA256}"
                    " /tmp/zizmor.tar.gz | sha256sum --check --strict -\n"
                    "tar -xzf /tmp/zizmor.tar.gz -C /tmp\n"
                    "sudo install -m 0755 /tmp/zizmor /usr/local/bin/zizmor\n"
                    "zizmor --version\n"
                    f"{PROJEN_RUN} {security_git_hub_actions_scan.name}"
                ),
            ),
            JobStep(
                name="SCA (multi)",
                background=True,
                run=(
                    "curl -fsSL -o /tmp/osv-scanner "
                    "https://github.com/google/osv-scanner/releases/download/"
                    f"v{OSV_SCANNER_VERSION}/osv-scanner_linux_amd64\n"
                    f"printf '%s  %s\\n' {OSV_SCANNER_LINUX_AMD64_SHA256}"
                    " /tmp/osv-scanner | sha256sum --check --strict -\n"
                    "sudo install -m 0755 /tmp/osv-scanner "
                    "/usr/local/bin/osv-scanner\n"
                    "osv-scanner --version\n"
                    f"{PROJEN_RUN} {security_sca_multi.name}"
                ),
            ),
            JobStep(
                name="Dockerfile scan",
                background=True,
                run=(
                    "curl -fsSL -o /tmp/hadolint "
                    "https://github.com/hadolint/hadolint/releases/download/"
                    f"v{HADOLINT_VERSION}/hadolint-linux-x86_64\n"
                    f"printf '%s  %s\\n' {HADOLINT_LINUX_X86_64_SHA256}"
                    " /tmp/hadolint | sha256sum --check --strict -\n"
                    "sudo install -m 0755 /tmp/hadolint "
                    "/usr/local/bin/hadolint\n"
                    "hadolint --version\n"
                    f"{PROJEN_RUN} {security_dockerfile_lint.name}"
                ),
            ),
            JobStep(wait_all=True),
        ],
    ),
)


project.synth()
