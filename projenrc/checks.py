"""Static checks: ruff, ty, and their projen tasks."""

from typing import Final, TypedDict

from projen import Task, TomlFile
from projen.awscdk import AwsCdkPythonApp

from projenrc.common import PYTHON_VERSION, ConfigFileSpec, JsonValue

RUFF_IGNORED_RULES: Final[list[JsonValue]] = [
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
]


CHECKS_CONFIG_FILES: Final[list[ConfigFileSpec]] = [
    # Ruff configuration - projen-managed.
    {
        "path": "ruff.toml",
        "kind": "toml",
        "obj": {
            "target-version": f"py{PYTHON_VERSION.replace('.', '')}",
            "line-length": 88,
            "lint": {
                "preview": True,
                "select": ["ALL"],
                "ignore": RUFF_IGNORED_RULES,
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
    },
    # ty configuration - projen-managed.
    {
        "path": "ty.toml",
        "kind": "toml",
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
]


class ChecksTasks(TypedDict):
    """Tasks created by :func:`create_checks`."""

    lint: Task
    format_check: Task
    typecheck: Task
    check: Task


def create_checks(project: AwsCdkPythonApp) -> ChecksTasks:
    """Configure ruff, ty, pre-commit, and static-check tasks.

    Args:
        project: The projen project.

    Returns:
        The created static-check tasks.
    """
    for spec in CHECKS_CONFIG_FILES:
        TomlFile(project, spec["path"], obj=spec["obj"])

    lint = project.add_task("lint", description="Lint with ruff", exec="ruff check .")
    project.add_task(
        "lint:fix",
        description="Autofix ruff violations (safe fixes only)",
        exec="ruff check --fix .",
    )
    project.add_task(
        "format", description="Format code with ruff", exec="ruff format ."
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

    return ChecksTasks(
        lint=lint,
        format_check=format_check,
        typecheck=typecheck,
        check=check,
    )
