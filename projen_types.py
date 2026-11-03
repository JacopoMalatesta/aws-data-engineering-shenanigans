"""Type vocabulary shared by ``.projenrc.py``, ``projen_config.py`` and ``constants.py``.

This module declares types only. It never creates projen resources and
holds no configuration values.
"""

from enum import StrEnum
from typing import Literal, NotRequired, TypedDict

type JsonValue = str | int | bool | list[JsonValue] | dict[str, JsonValue] | None


class FileType(StrEnum):
    """Kind of managed file."""

    JSON = "JSON"
    TOML = "TOML"
    YAML = "YAML"
    TEXT = "TEXT"
    OTHER = "OTHER"


class TextFileSpec(TypedDict):
    """Plain-text projen-managed file, rendered verbatim from ``lines``.

    Needed for formats whose exact text projen's serializers would alter
    (projen's INI writer quotes values containing spaces, which pytest
    rejects when parsing ``addopts``).
    """

    file_path: str
    file_type: Literal[FileType.TEXT]
    lines: list[str]
    marker: NotRequired[bool]


class StandardFileSpec(TypedDict):
    """Structure-backed projen-managed file rendered from ``obj``."""

    file_path: str
    file_type: Literal[FileType.JSON, FileType.TOML, FileType.YAML, FileType.OTHER]
    obj: dict[str, JsonValue]
    marker: NotRequired[bool]


type FileSpec = StandardFileSpec | TextFileSpec


class TaskName(StrEnum):
    """Name of a projen task used by this repo's tooling.

    Values are the task names; members are scope labels (``PYTHON_*``
    Python-source quality gates, ``CDK_*`` ``cdk`` CLI wrappers,
    ``SECURITY_*`` repo and lockfile scans). ``CDK_*``, ``TEST`` and
    ``PACKAGE`` are projen built-ins; the rest are declared in
    ``PROJEN_TASKS``. Unlisted built-ins (``destroy``, ``watch``) are
    intentional. Step labels live in ``JobStepName``.
    """

    CDK_DEPLOY = "deploy"
    CDK_DIFF = "diff"
    PYTHON_CHECK = "check"
    PYTHON_FORMAT = "format"
    PYTHON_FORMAT_CHECK = "format:check"
    PYTHON_LINT = "lint"
    PYTHON_LINT_FIX = "lint:fix"
    PACKAGE = "package"
    SECURITY = "security"
    SECURITY_DOCKERFILE_LINT = "security:dockerfile-lint"
    SECURITY_GITHUB_ACTIONS_SCAN = "security:git-hub-actions-scan"
    SECURITY_IAC_SCAN = "security:iac-scan"
    SECURITY_MISCONFIG_SCAN = "security:misconfig-scan"
    SECURITY_SAST = "security:sast"
    SECURITY_SCA_MULTI_LANGUAGE = "security:sca-multi-language"
    SECURITY_SCA_PYTHON = "security:sca-python"
    SECURITY_SECRET_SCAN = "security:secret-scan"  # ruff: ignore[hardcoded-password-string]
    PYTHON_STATIC_ANALYSIS = "static-analysis"
    CDK_SYNTH = "synth"
    CDK_SYNTH_SILENT = "synth:silent"
    TEST = "test"
    PYTHON_TYPECHECK = "typecheck"


class ProjenTaskSpec(TypedDict):
    """Specification for a projen task.

    ``exec`` and ``spawns`` are optional. ``spawns`` lists the tasks passed
    to ``Task.spawn``, in spawn order; ``Task.spawn`` needs the spawned task
    to already exist when it is called, so every spawned task must be
    declared in ``PROJEN_TASKS`` before the task that spawns it. A task may
    carry both an ``exec`` and ``spawns``.
    """

    name: TaskName
    description: str
    exec: NotRequired[str]
    spawns: NotRequired[list[TaskName]]


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


class WorkflowName(StrEnum):
    """Name of a GitHub Actions workflow managed by this project."""

    BUILD = "build"
    DEPLOY = "deploy"
    SECURITY = "security"


class EnvironmentName(StrEnum):
    """Name of a deployment environment: one AWS account in one region."""

    DEV = "dev"


class JobName(StrEnum):
    """Identifier of a job within the managed workflows.

    Values render as the YAML job keys; provide distinct values for
    distinct jobs. A job may be referenced by more than one workflow.
    """

    BUILD = "build"
    CHECK = "check"
    DEPLOY = "deploy"
    SCAN = "scan"


class JobStepName(StrEnum):
    """Addressable step entry in ``GITHUB_JOB_STEPS``.

    Values are the rendered YAML ``name`` labels and must stay unique
    (shared values collapse steps). Members are scope labels under the
    same conventions as ``TaskName``. ``INSTALL_NODE``/``INSTALL_UV`` use
    official ``setup-*`` actions; other ``INSTALL_*`` steps are shell
    installs (``uses:`` vs ``run:`` in each spec).
    """

    AWS_CREDENTIALS = "AWS credentials via OIDC"
    CDK_DEPLOY = "CDK deploy"
    CDK_DIFF = "CDK diff"
    CDK_DIFF_CAPTURE = "CDK diff capture"
    CDK_SYNTH = "CDK synth"
    CHECKOUT = "Checkout repository"
    DOCKERFILE_SCAN = "Dockerfile scan"
    PYTHON_FORMAT_CHECK = "Python format check"
    GITHUB_ACTIONS_SCAN = "GitHub Actions scan"
    IAC_SCAN = "IaC scan"
    INSTALL_CDK_CLI = "Install CDK CLI"
    INSTALL_PYTHON_DEPENDENCIES = "Install Python dependencies"
    INSTALL_PROJEN_CLI = "Install projen CLI"
    PYTHON_LINT = "Python lint"
    MISCONFIG_SCAN = "Misconfig scan"
    PYTHON_PACKAGE = "Package Python code"
    POST_CDK_DIFF = "Post CDK diff"
    REGENERATE_PROJEN_FILES = "Regenerate projen files"
    SAST_SCAN = "SAST scan"
    SCA_MULTI_LANGUAGE = "SCA multi-language"
    SCA_PYTHON = "SCA Python"
    SECRET_SCAN = "Secret scan"  # ruff: ignore[hardcoded-password-string] - YAML step label, not a credential
    INSTALL_NODE = "Install Node"
    INSTALL_UV = "Install uv"
    PYTHON_STATIC_ANALYSIS = "Python static analysis"
    PYTHON_TYPECHECK = "Python typecheck"
    PYTHON_UNIT_TESTS = "Python unit tests"
    WAIT_FOR_SCANS = "Wait for scans"


class GitHubPermission(StrEnum):
    """Repository permission granted to a workflow job."""

    READ = "read"
    WRITE = "write"


class DeploymentEnvironment(TypedDict):
    """One deployment environment: a unique AWS account ID and region name.

    Consumed by ``app.py`` (one stack per environment) and rendered 1:1 into
    ``strategy.matrix.include`` of the GitHub jobs that assume the
    environment's OIDC role and run ``cdk diff``/``cdk deploy``.
    """

    environment_name: EnvironmentName
    aws_account_id: str
    region_name: str


class GitHubJobSpec(TypedDict):
    """Specification for a single job within a workflow.

    ``steps`` renders into the YAML job in list order. ``needs`` and
    ``matrix`` render as the job's ``needs`` and ``strategy.matrix.include``.
    """

    id: JobName
    runs_on: list[str]
    permissions: dict[str, GitHubPermission]
    steps: list[JobStepName]
    needs: NotRequired[list[JobName]]
    matrix: NotRequired[list[DeploymentEnvironment]]


class WorkflowTriggers(TypedDict):
    """GitHub Actions ``on`` triggers for one workflow.

    Keys mirror the keyword parameters of ``GithubWorkflow.on``. The
    mapping is closed: adding an event means adding a ``NotRequired``
    field whose value type must stay assignable to the matching
    ``GithubWorkflow.on`` parameter.
    """

    pull_request: NotRequired[dict[str, JsonValue]]
    push: NotRequired[dict[str, JsonValue]]
    workflow_dispatch: NotRequired[dict[str, JsonValue]]


class GitHubWorkflowSpec(TypedDict):
    """Specification for one GitHub Actions workflow file.

    ``on`` is a closed, event-keyed trigger mapping (``WorkflowTriggers``).
    Both type checkers verify every key against ``GithubWorkflow.on``'s
    keyword parameters, and projen still rejects unknown events at synth
    time, so no extra validation is needed. ``jobs`` references job specs
    from ``GITHUB_JOBS`` by id.
    """

    name: WorkflowName
    on: WorkflowTriggers
    jobs: list[JobName]


class GitHubJobStepSpec(TypedDict):
    """Specification for a registered GitHub Actions job step.

    ``name`` is the lookup key in ``STEPS_BY_NAME`` and doubles as the YAML
    display label (via the ``JobStepName`` value). All other fields mirror
    ``JobStep`` keyword arguments and are splatted as-is.
    """

    name: JobStepName
    run: NotRequired[str]
    uses: NotRequired[str]
    with_: NotRequired[dict[str, JsonValue]]
    env: NotRequired[dict[str, str]]
    background: NotRequired[bool]
    wait_all: NotRequired[bool]
