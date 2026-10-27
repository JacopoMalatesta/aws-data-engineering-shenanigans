"""Single source of truth for the AWS environment this repo deploys to."""

from typing import Final

# Referenced by app.py and read by the deploy workflow at runtime.
# Bare Final lets type checkers infer the type from the literal.
AWS_ACCOUNT_ID: Final = "925000840053"
AWS_REGION: Final = "eu-west-1"
