"""Projen project definition - the single source of truth for this repo.

Edit this file, then re-run it (``npx projen``) to regenerate every
projen-managed file. Never hand-edit those; they are read-only.
"""

from projen import TextFile
from projen.awscdk import AwsCdkPythonApp
from projen.github import GitHubOptions, PullRequestLintOptions, SemanticTitleOptions

from projenrc.checks import create_checks
from projenrc.common import PROJEN_VERSION, PYTHON_VERSION
from projenrc.local_tooling import create_local_tooling
from projenrc.security import create_security
from projenrc.workflows import create_workflows

project = AwsCdkPythonApp(
    author_email="jacopomalatesta95@gmail.com",
    author_name="JacopoMalatesta",
    cdk_version="2.275.0",
    dev_deps=[
        "pre-commit@4.6.2",
        "ruff@0.17.2",
        "ty@0.0.92",
        f"projen@{PROJEN_VERSION}",
    ],
    module_name="aws_data_engineering_shenanigans",
    name="aws-data-engineering-shenanigans",
    pytest_options={"version": "9.0.3"},
    uv=True,
    uv_options={
        "python_exec": PYTHON_VERSION,
        "project": {
            "name": "aws-data-engineering-shenanigans",
            "requires_python": (
                f">={PYTHON_VERSION},<{int(PYTHON_VERSION.split('.')[0]) + 1}.0"
            ),
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

project.add_git_ignore(".opencode/")
project.add_git_ignore("*.swp")

TextFile(
    project,
    "setup.cfg",
    lines=[
        "[options]",
        "packages = aws_data_engineering_shenanigans",
    ],
    readonly=False,
)

checks_tasks = create_checks(project)
create_local_tooling(project)
security_tasks = create_security(project)
workflows = create_workflows(
    project, checks_tasks=checks_tasks, security_tasks=security_tasks
)

project.synth()
