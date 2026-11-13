#!/usr/bin/env bash
# Edit or post the cdk-diff summary comment on the current pull request.
# Env: GH_REPO, GH_TOKEN, PR_NUMBER (injected by the build workflow).
set -euo pipefail

GH_REPO="${GH_REPO:?GH_REPO must be set}"
export GH_TOKEN="${GH_TOKEN:?GH_TOKEN must be set}"
PR_NUMBER="${PR_NUMBER:?PR_NUMBER must be set}"

DIFF_BODY_FILE=cdk-diff-comment.md
{
  echo '<!-- cdk-diff -->'
  echo '## 📋 cdk diff'
  if [[ -s cdk-diff.txt ]]; then
    echo '```text'
    cat cdk-diff.txt
    echo '```'
  else
    echo '✅ No infrastructure changes.'
  fi
} >"${DIFF_BODY_FILE}"
# Edit only the marked cdk-diff comment (--edit-last would rewrite the
# reviewer's trigger comment); post fresh if none found.
# Search every comment page (--paginate applies the filter per page, so the
# last-id pick happens in bash across the flattened stream).
COMMENT_ID="$(gh api --paginate "repos/${GH_REPO}/issues/${PR_NUMBER}/comments?per_page=100" --jq '
  .[]
  | select(
    .user.login == "github-actions[bot]"
    and (.body | contains("<!-- cdk-diff -->"))
  )
  | .id' | tail -n1)"
if [[ -n "${COMMENT_ID}" ]]; then
  gh api -X PATCH "repos/${GH_REPO}/issues/comments/${COMMENT_ID}" -F body=@"${DIFF_BODY_FILE}" >/dev/null
else
  gh api -X POST "repos/${GH_REPO}/issues/${PR_NUMBER}/comments" -F body=@"${DIFF_BODY_FILE}" >/dev/null
fi
