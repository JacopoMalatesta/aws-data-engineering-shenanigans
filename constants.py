"""Single source of truth for repo-wide constants.

Environment, tool and workflow constants, plus the shell snippets that the
CI workflows run. Consumed by ``.projenrc.py``, ``projen_config.py`` and
``app.py``, and read by the deploy workflow at runtime.
"""

from typing import Final

AWS_ACCOUNT_ID: Final = "925000840053"
AWS_REGION: Final = "eu-west-1"

PYTHON_VERSION: Final = "3.13"
NODE_VERSION: Final = "24"
PROJEN_RUN: Final = "npx projen@0.104.17"

EXPORT_AWS_ACCOUNT_ID_AND_REGION: Final[
    str
] = """echo "AWS_ACCOUNT_ID=$(uv run python -c 'from constants import AWS_ACCOUNT_ID; print(AWS_ACCOUNT_ID)')" >> "$GITHUB_ENV"
echo "AWS_REGION=$(uv run python -c 'from constants import AWS_REGION; print(AWS_REGION)')" >> "$GITHUB_ENV"
"""

POST_CDK_DIFF: Final[str] = """\
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

# flake8-plugin ruleset codes for the ruff ignore list.
AIRFLOW_RUFF_RULESET: Final = "AIR"
DJANGO_RUFF_RULESET: Final = "DJ"
FASTAPI_RUFF_RULESET: Final = "FAST"
NUMPY_RUFF_RULESET: Final = "NPY"
PANDAS_RUFF_RULESET: Final = "PD"

PRE_COMMIT_LANGUAGE_UNSUPPORTED: Final = "unsupported"
VIRTUAL_ENV_BINARY_DIR: Final = "./.venv/bin/"
