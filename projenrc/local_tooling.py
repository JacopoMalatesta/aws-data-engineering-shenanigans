"""Local developer tooling: editor integration and git hooks."""

from typing import Final, NotRequired, TypedDict, cast

from projen import YamlFile
from projen.awscdk import AwsCdkPythonApp
from projen.vscode import VsCode

from projenrc.common import JsonValue, get_task_by_name


class PreCommitHookSpec(TypedDict):
    """A single hook entry in ``.pre-commit-config.yaml``."""

    id: str
    name: str
    entry: str
    args: list[str]
    language: str
    types_or: NotRequired[list[str]]
    pass_filenames: NotRequired[bool]
    files: NotRequired[str]


PRE_COMMIT_HOOKS: Final[list[PreCommitHookSpec]] = [
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
]


PRE_COMMIT_CONFIG: Final[dict[str, JsonValue]] = {
    "repos": [
        {
            "repo": "local",
            "hooks": cast("list[JsonValue]", PRE_COMMIT_HOOKS),
        }
    ]
}


def create_local_tooling(project: AwsCdkPythonApp) -> None:
    """Configure VS Code and install git hooks during dependency setup.

    Args:
        project: The projen project.
    """
    YamlFile(
        project,
        ".pre-commit-config.yaml",
        obj=PRE_COMMIT_CONFIG,
    )

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

    install_task = get_task_by_name(project, "install")
    install_task.exec("pre-commit install")
