"""Projen project definition - the single source of truth for this repo.

Edit this file, then re-run it (``npx projen``) to regenerate every
projen-managed file. Never hand-edit those; they are read-only.
"""

from typing import Final

from projen import Task, YamlFile
from projen.awscdk import AwsCdkPythonApp
from projen.github import GitHubOptions, PullRequestLintOptions, SemanticTitleOptions
from projen.github.workflows import Job, JobPermission, JobStep
from projen.vscode import VsCode

# Shared with both uv_options and the CI setup-uv step in SETUP_STEPS.
PYTHON_VERSION: Final = "3.13"

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

# One-command entry point for static checks (local use; CI runs each
# check as a separate workflow step instead). Intentionally static-only:
# pytest runs via the `test` task, locally and in CI.
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
#
# Task lookup helper: `tasks.try_find` returns `Task | None`; several
# callers below need a hard guarantee, so the narrowing lives here
# instead of being repeated (ty flags `.name` on a possible None).


def _require_task(name: str) -> Task:
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


install_task = _require_task("install")
install_task.exec("pre-commit install")

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
# GitHub Actions
# Both workflows share their environment setup and their static check
# steps via the constants below, so no step is defined twice. Values
# that appear more than once are module-level constants (PROJEN_RUN,
# PYTHON_VERSION); single-use values stay inline in SETUP_STEPS.
# `projen build` is deliberately NOT used in CI: its aggregated phase
# chain (synth, test, packaging) conflicts with the granular-steps
# preference, so CI runs the individual tasks instead. The
# "Regenerate projen files" step reproduces the regeneration that the
# old `projen build` step performed via its default (first) phase.
# ------------------------------------------------------------------
PROJEN_RUN: Final = "npx projen@0.104.17"

github = project.github
if github is None:
    msg = "github workflows should be enabled for this project"
    raise RuntimeError(msg)

SETUP_STEPS: Final = [
    JobStep(uses="actions/checkout@v4"),
    JobStep(uses="astral-sh/setup-uv@v5", with_={"python-version": PYTHON_VERSION}),
    JobStep(uses="actions/setup-node@v4", with_={"node-version": "22"}),
    JobStep(name="Install CDK CLI", run="npm install -g aws-cdk@2.1146.1"),
    JobStep(name="Install dependencies", run="uv sync --frozen"),
]

# Task-name derivation requires this list to be defined after the
# lint/format:check/typecheck task objects exist (see checks section).
CHECK_STEPS: Final = [
    JobStep(name="Lint", run=f"{PROJEN_RUN} {lint.name}"),
    JobStep(name="Format check", run=f"{PROJEN_RUN} {format_check.name}"),
    JobStep(name="Type check", run=f"{PROJEN_RUN} {typecheck.name}"),
]

# ------------------------------------------------------------------
# GitHub Actions: build + synth + tests on every pull request
# ------------------------------------------------------------------
build = github.add_workflow("build")
build.on(pull_request={})
build.add_job(
    "build",
    Job(
        runs_on=["ubuntu-latest"],
        permissions={"contents": JobPermission.READ},
        steps=[
            *SETUP_STEPS,
            JobStep(name="Regenerate projen files", run=PROJEN_RUN),
            *CHECK_STEPS,
            JobStep(
                name="Unit tests",
                run=f"{PROJEN_RUN} {project.test_task.name}",
            ),
            JobStep(
                name="Synth",
                run=f"{PROJEN_RUN} {_require_task('synth').name}",
            ),
            JobStep(
                name="Package",
                run=f"{PROJEN_RUN} {_require_task('package').name}",
            ),
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
            *SETUP_STEPS,
            *CHECK_STEPS,
            JobStep(
                name="Unit tests",
                run=f"{PROJEN_RUN} {project.test_task.name}",
            ),
            JobStep(name="Export constants from constants.py", run=EXPORT_CONSTANTS),
            JobStep(
                name="Configure AWS credentials via OIDC",
                uses="aws-actions/configure-aws-credentials@v4",
                with_={
                    "role-to-assume": "arn:aws:iam::${{ env.AWS_ACCOUNT_ID }}:role/github-actions-deploy",
                    "aws-region": "${{ env.AWS_REGION }}",
                },
            ),
            JobStep(
                name="Deploy stack",
                run=f"{PROJEN_RUN} {_require_task('deploy').name}",
            ),
        ],
    ),
)

project.synth()
