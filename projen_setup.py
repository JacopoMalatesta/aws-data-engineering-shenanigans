"""Assembly of the projen project from the ``projen_config.py`` data.

This module holds all behavior that used to live in ``.projenrc.py``.
The public entry point is :func:`set_up_project`; everything else is
private by convention because the only caller is that entry shim.
"""

from typing import TYPE_CHECKING, Final, cast

from projen import JsonFile, ObjectFile, Task, TomlFile, YamlFile
from projen.awscdk import AwsCdkPythonApp
from projen.github import (
    GitHubOptions,
    GithubWorkflow,
    PullRequestLintOptions,
    SemanticTitleOptions,
)
from projen.github.workflows import (
    Job,
    JobMatrix,
    JobPermission,
    JobStep,
    JobStrategy,
)
from projen.vscode import VsCode

from constants import CDK_NAG_VERSION, PYTHON_VERSION
from projen_config import (
    DEV_DEPS,
    GIT_IGNORE_PATTERNS,
    GITHUB_WORKFLOWS,
    PROJECT_FILES,
    PROJECT_SPEC,
    PROJEN_TASKS,
    PYPROJECT_TOOL_SECTIONS,
    SEMANTIC_TITLE_TYPES,
    VSCODE_EXTENSIONS,
    VSCODE_SETTINGS,
)
from projen_types import FileType, GitHubPermission, TaskName

if TYPE_CHECKING:
    from collections.abc import Mapping


class UndeclaredSubtaskError(KeyError):
    """A ``ProjenTaskSpec`` spawns a task neither declared nor built-in."""


class UndeclaredJobError(KeyError):
    """A ``GitHubJobSpec`` needs a job absent from its own workflow."""


class MissingPyprojectTomlError(KeyError):
    """The ``pyproject.toml`` file component is absent from the project."""


FILE_CLASSES: Final[dict[FileType, type[ObjectFile]]] = {
    FileType.JSON: JsonFile,
    FileType.TOML: TomlFile,
    FileType.YAML: YamlFile,
    FileType.OTHER: ObjectFile,
}

PERMISSION_CLASSES: Final[dict[GitHubPermission, JobPermission]] = {
    GitHubPermission.READ: JobPermission.READ,
    GitHubPermission.WRITE: JobPermission.WRITE,
}


def set_up_project() -> None:
    """Assemble the full project from ``projen_config.py`` and synth it."""
    project = _create_project()
    _configure_pyproject(project)
    _add_project_files(project)
    _add_tasks(project)
    _configure_editor_tooling(project)
    _add_github_workflows(project)
    project.synth()


def _create_project() -> AwsCdkPythonApp:
    """Instantiate the app, register the cdk-nag dependency, apply lint options.

    Returns:
        The freshly created CDK Python app.
    """
    project = AwsCdkPythonApp(
        author_email=PROJECT_SPEC["author_email"],
        author_name=PROJECT_SPEC["author_name"],
        cdk_version=PROJECT_SPEC["cdk_version"],
        dev_deps=DEV_DEPS,
        module_name=PROJECT_SPEC["module_name"],
        name=PROJECT_SPEC["name"],
        pytest_options={"version": PROJECT_SPEC["pytest_version"]},
        uv=True,
        uv_options={
            "python_exec": PYTHON_VERSION,
            "project": {
                "name": PROJECT_SPEC["name"],
                "requires_python": (
                    f">={PYTHON_VERSION},<{int(PYTHON_VERSION.split('.')[0]) + 1}.0"
                ),
            },
        },
        version=PROJECT_SPEC["version"],
        github_options=GitHubOptions(
            pull_request_lint_options=PullRequestLintOptions(
                semantic_title_options=SemanticTitleOptions(
                    types=SEMANTIC_TITLE_TYPES,
                ),
            ),
        ),
    )
    project.add_dependency(f"cdk-nag@{CDK_NAG_VERSION}")
    return project


def _configure_pyproject(project: AwsCdkPythonApp) -> None:
    """Inject ``PYPROJECT_TOOL_SECTIONS`` into the Uv-managed pyproject.toml.

    ``add_override`` merges on top of projen's serialized pyproject schema,
    so tool sections that projen does not whitelist (e.g. ``basedpyright``)
    still render into the generated file.

    Raises:
        MissingPyprojectTomlError: If the pyproject.toml component is missing.
    """
    pyproject = project.try_find_object_file("pyproject.toml")
    if pyproject is None:
        msg = (
            "pyproject.toml should exist for uv-based projects; the Uv "
            "component created by AwsCdkPythonApp is missing or disabled"
        )
        raise MissingPyprojectTomlError(msg)
    for name, section in PYPROJECT_TOOL_SECTIONS.items():
        pyproject.add_override(f"tool.{name}", section)


def _add_project_files(project: AwsCdkPythonApp) -> None:
    """Append git ignore patterns and render the projen-managed files."""
    for ignore_pattern in GIT_IGNORE_PATTERNS:
        project.add_git_ignore(ignore_pattern)

    for file_path, file_spec in PROJECT_FILES.items():
        _ = FILE_CLASSES[file_spec["file_type"]](
            scope=project,
            file_path=file_path,
            obj=file_spec["obj"],
            marker=file_spec.get("marker"),
        )


def _add_tasks(project: AwsCdkPythonApp) -> None:
    """Declare ``PROJEN_TASKS``, resolve spawns and wire pre-commit.

    Pass one registers every spec, replacing any projen built-in that
    carries the same name; pass two resolves ``spawns``, so config order
    is free and subtasks may be any project task, declared in
    ``PROJEN_TASKS`` or a projen built-in.

    Raises:
        UndeclaredSubtaskError: If a spawned task is neither declared
            nor a built-in.
    """
    tasks_by_name: dict[TaskName, Task] = {}
    for task_name, task_spec in PROJEN_TASKS.items():
        if project.tasks.try_find(task_name) is not None:
            _ = project.tasks.remove_task(task_name)
        tasks_by_name[task_name] = project.add_task(
            task_name,
            description=task_spec["description"],
            exec=task_spec.get("exec"),
        )

    for task_name, task_spec in PROJEN_TASKS.items():
        task = tasks_by_name[task_name]
        for subtask_name in task_spec.get("spawns", []):
            subtask = project.tasks.try_find(subtask_name)
            if subtask is None:
                msg = (
                    f"task '{task_name}' spawns undeclared task "
                    f"'{subtask_name}'; declare it in PROJEN_TASKS "
                    "or spawn a built-in task"
                )
                raise UndeclaredSubtaskError(msg)
            task.spawn(subtask)

    # Install git hooks as part of dependency setup.
    install_task = project.tasks.try_find("install")
    if install_task is not None:
        install_task.exec("pre-commit install")
        install_task.exec("pre-commit install --hook-type commit-msg")


def _configure_editor_tooling(project: AwsCdkPythonApp) -> None:
    """Recommend extensions and apply the shared VS Code settings."""
    vscode = VsCode(project)
    for extension in VSCODE_EXTENSIONS:
        vscode.extensions.add_recommendations(extension)
    vscode.settings.add_settings(VSCODE_SETTINGS)


def _add_github_workflows(project: AwsCdkPythonApp) -> None:
    """Register the configured workflows and their inline jobs.

    Raises:
        RuntimeError: If GitHub integration is disabled for the project.
        UndeclaredJobError: If a job's ``needs`` lists a job absent from
            its own workflow.
    """
    github = project.github
    if github is None:
        msg = "github workflows should be enabled for this project"
        raise RuntimeError(msg)

    for workflow_name, workflow_spec in GITHUB_WORKFLOWS.items():
        workflow = GithubWorkflow(
            github,
            workflow_name,
            limit_concurrency=workflow_spec.get("limit_concurrency", False),
        )
        workflow.on(**workflow_spec["on"])
        for job_name, job_spec in workflow_spec["jobs"].items():
            if any(
                need not in workflow_spec["jobs"] for need in job_spec.get("needs", [])
            ):
                msg = (
                    f"job '{job_name}' needs a sibling job absent from "
                    "the same workflow's jobs mapping"
                )
                raise UndeclaredJobError(msg)

            matrix_entries = job_spec.get("matrix")
            if matrix_entries is None:
                strategy = None
            else:
                strategy = JobStrategy(
                    matrix=JobMatrix(
                        # Sound cast: the entries serialize as plain string
                        # mappings; jsii's JobMatrix only accepts those.
                        include=cast("list[Mapping[str, str]]", matrix_entries)
                    ),
                    fail_fast=job_spec.get("fail_fast"),
                    max_parallel=job_spec.get("max_parallel"),
                )
            workflow.add_job(
                job_name,
                Job(
                    runs_on=job_spec["runs_on"],
                    permissions={
                        scope: PERMISSION_CLASSES[level]
                        for scope, level in job_spec["permissions"].items()
                    },
                    steps=[
                        JobStep(name=step_name, **step_spec)
                        for step_name, step_spec in job_spec["steps"].items()
                    ],
                    needs=job_spec.get("needs"),
                    strategy=strategy,
                ),
            )
