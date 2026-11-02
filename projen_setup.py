"""Assembly of the projen project from the ``projen_config.py`` data.

This module holds all behavior that used to live in ``.projenrc.py``.
The public entry point is :func:`set_up_project`; everything else is
private by convention because the only caller is that entry shim.
"""

from typing import Final

from projen import JsonFile, ObjectFile, Task, TomlFile, YamlFile
from projen.awscdk import AwsCdkPythonApp
from projen.github import GitHubOptions, PullRequestLintOptions, SemanticTitleOptions
from projen.github.workflows import Job, JobPermission, JobStep
from projen.vscode import VsCode

from constants import PYTHON_VERSION
from projen_config import (
    DEV_DEPS,
    GIT_IGNORE_PATTERNS,
    GITHUB_JOB_STEPS,
    GITHUB_WORKFLOWS,
    PROJECT_FILES,
    PROJECT_SPEC,
    PROJEN_TASKS,
    SEMANTIC_TITLE_TYPES,
    VSCODE_EXTENSIONS,
    VSCODE_SETTINGS,
)
from projen_types import FileType, GitHubPermission, JobStepName, TaskName


class UndeclaredSubtaskError(KeyError):
    """A ``ProjenTaskSpec`` spawns a task with no declared spec (yet)."""


class UndeclaredStepError(KeyError):
    """A ``GitHubJobSpec`` references a step absent from ``GITHUB_JOB_STEPS``."""


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
    _add_project_files(project)
    _add_tasks(project)
    _configure_editor_tooling(project)
    _add_github_workflows(project)
    project.synth()


def _create_project() -> AwsCdkPythonApp:
    """Instantiate the app and its config-level GitHub lint options.

    Returns:
        The freshly created CDK Python app.
    """
    return AwsCdkPythonApp(
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


def _add_project_files(project: AwsCdkPythonApp) -> None:
    """Append git ignore patterns and render the projen-managed files."""
    for ignore_pattern in GIT_IGNORE_PATTERNS:
        project.add_git_ignore(ignore_pattern)

    for file_spec in PROJECT_FILES:
        _ = FILE_CLASSES[file_spec["file_type"]](
            scope=project,
            file_path=file_spec["file_path"],
            obj=file_spec["obj"],
            marker=file_spec.get("marker"),
        )


def _add_tasks(project: AwsCdkPythonApp) -> None:
    """Declare ``PROJEN_TASKS`` and wire ``pre-commit install``.

    ``Task.spawn`` needs the spawned task to exist when it is called, so
    ``PROJEN_TASKS`` must declare every spawned task before the task that
    spawns it.

    Raises:
        UndeclaredSubtaskError: If a task spawns an undeclared subtask.
    """
    tasks_by_name: dict[TaskName, Task] = {}
    for task_spec in PROJEN_TASKS:
        tasks_by_name[task_spec["name"]] = project.add_task(
            task_spec["name"],
            description=task_spec["description"],
            exec=task_spec.get("exec"),
        )
        task = tasks_by_name[task_spec["name"]]
        for subtask_name in task_spec.get("spawns", []):
            subtask = tasks_by_name.get(subtask_name)
            if subtask is None:
                msg = (
                    f"task '{task_spec['name']}' spawns undeclared task "
                    f"'{subtask_name}'; declare every spawned task in "
                    "PROJEN_TASKS before the task that spawns it"
                )
                raise UndeclaredSubtaskError(msg)
            task.spawn(subtask)

    # Install git hooks as part of dependency setup.
    install_task = project.tasks.try_find("install")
    if install_task is not None:
        install_task.exec("pre-commit install")


def _configure_editor_tooling(project: AwsCdkPythonApp) -> None:
    """Recommend extensions and apply the shared VS Code settings."""
    vscode = VsCode(project)
    for extension in VSCODE_EXTENSIONS:
        vscode.extensions.add_recommendations(extension)
    vscode.settings.add_settings(VSCODE_SETTINGS)


def _add_github_workflows(project: AwsCdkPythonApp) -> None:
    """Register the configured workflows, jobs, and addressable steps.

    Raises:
        RuntimeError: If GitHub integration is disabled for the project.
        UndeclaredStepError: If a job references an undeclared step.
    """
    github = project.github
    if github is None:
        msg = "github workflows should be enabled for this project"
        raise RuntimeError(msg)

    steps_by_name: Final[dict[JobStepName, JobStep]] = {
        step_spec["name"]: JobStep(**step_spec) for step_spec in GITHUB_JOB_STEPS
    }

    for workflow_spec in GITHUB_WORKFLOWS:
        workflow = github.add_workflow(workflow_spec["name"])
        workflow.on(**workflow_spec["on"])
        for job_spec in workflow_spec["jobs"]:
            job_steps: list[JobStep] = []
            for step_name in job_spec["steps"]:
                step = steps_by_name.get(step_name)
                if step is None:
                    msg = (
                        f"job '{job_spec['id']}' references undeclared step "
                        f"'{step_name}'; declare every step in GITHUB_JOB_STEPS"
                    )
                    raise UndeclaredStepError(msg)
                job_steps.append(step)
            workflow.add_job(
                job_spec["id"],
                Job(
                    runs_on=job_spec["runs_on"],
                    permissions={
                        scope: PERMISSION_CLASSES[level]
                        for scope, level in job_spec["permissions"].items()
                    },
                    steps=job_steps,
                ),
            )
