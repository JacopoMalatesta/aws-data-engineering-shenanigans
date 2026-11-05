"""Single source of truth for repo-wide constants.

Tool and workflow constants, plus the shell snippets that the CI
workflows run. Consumed by ``.projenrc.py`` and ``projen_config.py``.
"""

from typing import Final

PYTHON_VERSION: Final = "3.13"
NODE_VERSION: Final = "24"
PROJEN_RUN: Final = "npx projen@0.104.17"

POST_CDK_DIFF: Final = """\
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
CDK_NAG_VERSION: Final = "3.0.2"

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

CHECKOUT_V7_PIN: Final = "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_UV_V10_PIN: Final = "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2"
SETUP_NODE_V7_PIN: Final = "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1"
AWS_CREDENTIALS_V6_PIN: Final = (
    "aws-actions/configure-aws-credentials@e1253824e5c10ff9df46874f81ed3ec929e19cfd"
)

# flake8-plugin ruleset codes for the ruff ignore list.
AIRFLOW_RUFF_RULESET: Final = "AIR"
DJANGO_RUFF_RULESET: Final = "DJ"
FASTAPI_RUFF_RULESET: Final = "FAST"
NUMPY_RUFF_RULESET: Final = "NPY"
PANDAS_RUFF_RULESET: Final = "PD"

PRE_COMMIT_LANGUAGE_UNSUPPORTED: Final = "unsupported"
VIRTUAL_ENV_BINARY_DIR: Final = "./.venv/bin/"
