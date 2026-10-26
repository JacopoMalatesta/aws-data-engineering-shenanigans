from typing import Final

# The single source of truth for this deployment's AWS target.
# Referenced by app.py and read by the deploy workflow at runtime.
AWS_ACCOUNT_ID: Final[str] = "925000840053"
AWS_REGION: Final[str] = "eu-west-1"
