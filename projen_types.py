"""Type vocabulary shared by ``.projenrc.py``, ``projen_config.py`` and ``constants.py``.

This module declares types only. It never creates projen resources and
holds no configuration values.
"""

from enum import StrEnum
from typing import NotRequired, TypedDict

type JsonValue = str | int | bool | list[JsonValue] | dict[str, JsonValue] | None


class FileType(StrEnum):
    """Kind of managed file."""

    JSON = "JSON"
    TOML = "TOML"
    YAML = "YAML"
    OTHER = "OTHER"


class FileSpec(TypedDict):
    """Specification for a projen-managed file.

    ``PROJECT_FILES`` keys are the ``file_path``; ``file_type`` selects
    the projen file class and ``obj`` is the serialized document.
    """

    file_type: FileType
    obj: dict[str, JsonValue]
    marker: NotRequired[bool]


class TaskName(StrEnum):
    """Name of a projen task used by this repo's tooling.

    Values are the task names; members are scope labels (``PYTHON_*``
    Python-source quality gates, ``CDK_*`` ``cdk`` CLI wrappers,
    ``SECURITY_*`` repo and lockfile scans). ``CDK_DEPLOY``, ``CDK_DIFF``,
    ``CDK_SYNTH_SILENT``, ``TEST`` and ``PACKAGE`` are projen built-ins;
    ``CDK_SYNTH`` is a projen built-in whose behavior ``PROJEN_TASKS``
    overrides for strict synthesis; the rest are declared in
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

    ``PROJEN_TASKS`` keys are the task names. ``exec`` and ``spawns``
    are optional. ``spawns`` lists the task names passed to
    ``Task.spawn``, in spawn order; subtasks resolve in a second pass
    after every spec is registered, so config order is free and a
    subtask may be any project task, declared in ``PROJEN_TASKS`` or a
    projen built-in. A task may carry both an ``exec`` and ``spawns``.
    """

    description: str
    exec: NotRequired[str]
    spawns: NotRequired[list[TaskName]]


class PreCommitHookSpec(TypedDict):
    """A single hook entry in ``.pre-commit-config.yaml``.

    ``stages`` pins the hook to one stage (hooks without it run in
    every installed stage); ``additional_dependencies`` seeds
    pre-commit-managed environments such as ``language: node``;
    ``language_version`` selects that environment's runtime (``system``
    shares the PATH node, avoiding nodeenv downloads).
    """

    id: str
    name: str
    entry: str
    args: list[str]
    language: str
    types_or: NotRequired[list[str]]
    pass_filenames: NotRequired[bool]
    files: NotRequired[str]
    stages: NotRequired[list[str]]
    additional_dependencies: NotRequired[list[str]]
    language_version: NotRequired[str]


class WorkflowName(StrEnum):
    """Name of a GitHub Actions workflow managed by this project."""

    BUILD = "build"
    COMMIT_LINT = "commitlint"
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
    COMMIT_LINT = "commitlint"
    DEPLOY = "deploy"
    SCAN = "scan"


class JobStepName(StrEnum):
    """Addressable step entry in ``GITHUB_JOB_STEPS``.

    Values are the rendered YAML ``name`` labels and must stay unique
    (shared values collapse steps). Members are scope labels under the
    same conventions as ``TaskName``. ``CHECKOUT`` and
    ``CHECKOUT_FULL_HISTORY`` pin the official checkout action at
    default vs full fetch depth, ``INSTALL_NODE``/``INSTALL_UV`` use
    official ``setup-*`` actions; other ``INSTALL_*`` steps are shell
    installs (``uses:`` vs ``run:`` in each spec).
    """

    AWS_CREDENTIALS = "AWS credentials via OIDC"
    CDK_DEPLOY = "CDK deploy"
    CDK_DIFF = "CDK diff"
    CDK_DIFF_CAPTURE = "CDK diff capture"
    CDK_SYNTH = "CDK synth"
    CHECKOUT = "Checkout repository"
    CHECKOUT_FULL_HISTORY = "Checkout repository (full history)"
    COMMIT_LINT = "Commit message lint"
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

    ``GITHUB_JOBS`` keys are the job ids and double as the YAML job
    names. ``steps`` renders into the YAML job in list order. ``needs``
    and ``matrix`` render as the job's ``needs`` and
    ``strategy.matrix.include``. ``max_parallel`` and ``fail_fast``
    render into the same strategy block: ``max_parallel: 1`` runs the
    matrix legs one at a time, in include order, and ``fail_fast``
    cancels the remaining queued or in-progress legs on a failure.
    """

    runs_on: list[str]
    permissions: dict[str, GitHubPermission]
    steps: list[JobStepName]
    needs: NotRequired[list[JobName]]
    matrix: NotRequired[list[DeploymentEnvironment]]
    max_parallel: NotRequired[int]
    fail_fast: NotRequired[bool]


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

    ``GITHUB_WORKFLOWS`` keys are the workflow names. ``on`` is a
    closed, event-keyed trigger mapping (``WorkflowTriggers``).
    Both type checkers verify every key against ``GithubWorkflow.on``'s
    keyword parameters, and projen still rejects unknown events at synth
    time, so no extra validation is needed. ``jobs`` lists ``GITHUB_JOBS``
    keys. ``limit_concurrency`` enables the workflow's concurrency group,
    which projen defaults to the workflow name with ``cancel-in-progress:
    false`` — a second run queues behind the in-flight one.
    """

    on: WorkflowTriggers
    jobs: list[JobName]
    limit_concurrency: NotRequired[bool]


class GitHubJobStepSpec(TypedDict):
    """Specification for a registered GitHub Actions job step.

    ``GITHUB_JOB_STEPS`` keys are the YAML ``name`` labels (via the
    ``JobStepName`` value) and double as lookup keys; setup passes the
    key explicitly as ``JobStep``'s ``name`` argument. All other fields
    mirror ``JobStep`` keyword arguments and are splatted as-is.
    """

    run: NotRequired[str]
    uses: NotRequired[str]
    with_: NotRequired[dict[str, JsonValue]]
    env: NotRequired[dict[str, str]]
    background: NotRequired[bool]
    wait_all: NotRequired[bool]
