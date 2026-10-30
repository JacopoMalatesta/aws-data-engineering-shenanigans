"""Shared helpers and cross-cutting constants for projen configuration."""

from typing import Final, Literal, TypedDict

from projen import Task
from projen.awscdk import AwsCdkPythonApp

PYTHON_VERSION: Final = "3.13"
PROJEN_VERSION: Final = "0.104.17"

JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class ConfigFileSpec(TypedDict):
    """Specification for a projen-managed configuration file."""

    path: str
    kind: Literal["yaml", "toml"]
    obj: dict[str, JsonValue]


def get_task_by_name(project: AwsCdkPythonApp, name: str) -> Task:
    """Return a projen task by name.

    Args:
        project: The projen project.
        name: Registered task name.

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
