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
# Edit only the marked cdk-diff comment (--edit-last would rewrite the
# reviewer's trigger comment); post fresh if none found.
# Search every comment page (--paginate applies the filter per page, so the
# last-id pick happens in bash across the flattened stream).
COMMENT_ID="$(gh api --paginate "repos/$GH_REPO/issues/$PR_NUMBER/comments?per_page=100" --jq '
  .[]
  | select(
    .user.login == "github-actions[bot]"
    and (.body | contains("<!-- cdk-diff -->"))
  )
  | .id' | tail -n1)"
if [ -n "$COMMENT_ID" ]; then
  gh api -X PATCH "repos/$GH_REPO/issues/comments/$COMMENT_ID" -F body=@"$DIFF_BODY_FILE" > /dev/null
else
  gh api -X POST "repos/$GH_REPO/issues/$PR_NUMBER/comments" -F body=@"$DIFF_BODY_FILE" > /dev/null
fi
"""

CODE_RABBIT_IGNORE_TITLE_KEYWORDS: Final = ["WIP", "[skip review]", "DO NOT REVIEW"]
CODE_RABBIT_IGNORED_USERNAMES: Final = ["dependabot[bot]"]
_QUOTED_KEYWORDS: Final = " ".join(
    f'"{keyword}"' for keyword in CODE_RABBIT_IGNORE_TITLE_KEYWORDS
)
_BOT_LOGIN_CONDITION: Final = " || ".join(
    f'[ "$login" = "{username}" ]' for username in CODE_RABBIT_IGNORED_USERNAMES
)

# Trigger script for the PR reviewer workflow: reads the event payload
# from GITHUB_EVENT_PATH, applies the skip rules below, then comments
# "@coderabbitai review" (fresh comment per event — editing wouldn't re-trigger).
CODE_REVIEW_TRIGGER: Final = f"""\
action="$(jq -r '.action' "$GITHUB_EVENT_PATH")"
draft="$(jq -r '.pull_request.draft' "$GITHUB_EVENT_PATH")"
login="$(jq -r '.pull_request.user.login' "$GITHUB_EVENT_PATH")"
title="$(jq -r '.pull_request.title // ""' "$GITHUB_EVENT_PATH")"
title_change="$(jq -r '.changes.title // empty' "$GITHUB_EVENT_PATH")"
if [ "$action" = "edited" ] && [ -z "$title_change" ]; then
  echo "Skipping review trigger: edit did not change the title."
  exit 0
fi
if [ "$draft" = "true" ] || {_BOT_LOGIN_CONDITION}; then
  echo "Skipping review trigger: draft PR or ignored bot author."
  exit 0
fi
for keyword in {_QUOTED_KEYWORDS}; do
  if printf '%s' "$title" | grep -qiF -- "$keyword"; then
    echo "Skipping review trigger: PR title contains '$keyword'."
    exit 0
  fi
done
gh pr comment "$PR_NUMBER" --body "@coderabbitai review"
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

COMMITLINT_CLI_VERSION: Final = "21.2.4"
COMMITLINT_CONFIG_CONVENTIONAL_VERSION: Final = "21.2.4"
# commitlint rule severities: 0 = disabled, 1 = warn, 2 = error.
COMMITLINT_RULE_SEVERITY_ERROR: Final = 2
COMMITLINT_RULE_CONDITION_ALWAYS: Final = "always"

DEPTRY_RULE_MISPLACED_DEV_DEPENDENCY: Final = "DEP004"

ZIZMOR_VERSION: Final = "1.31.1"
OSV_SCANNER_VERSION: Final = "2.7.0"
HADOLINT_VERSION: Final = "2.15.1"
YAMLLINT_VERSION: Final = "1.38.0"
TAPLO_VERSION: Final = "0.10.0"
ZIZMOR_LINUX_X64_TARBALL_SHA256: Final = (
    "d185f726bdaf92df78273217dfdd24ebcd6b0ef48cf3ce776ff5762b6e138c99"
)
ACTIONLINT_VERSION: Final = "1.7.12"
ACTIONLINT_LINUX_AMD64_TARBALL_SHA256: Final = (
    "8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
)
TAPLO_LINUX_X64_GZIP_SHA256: Final = (
    "8fe196b894ccf9072f98d4e1013a180306e17d244830b03986ee5e8eabeb6156"
)
OSV_SCANNER_LINUX_AMD64_SHA256: Final = (
    "160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b"
)
HADOLINT_LINUX_X86_64_SHA256: Final = (
    "c7187db94eeeeca956519a6af171adc31453941a1e777961f6e680f697c8c507"
)

# Dependabot needs release-tag commits: untagged SHAs drift to the branch
# head (dependabot-core#14716). No "#" suffixes — projen would quote them,
# breaking the rendered ref.
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
PRE_COMMIT_LANGUAGE_NODE: Final = "node"
# Use the developer's PATH node instead of nodeenv-managed downloads.
PRE_COMMIT_LANGUAGE_VERSION_SYSTEM: Final = "system"
VIRTUAL_ENV_BINARY_DIR: Final = "./.venv/bin/"
