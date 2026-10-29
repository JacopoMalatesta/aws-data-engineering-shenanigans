"""Sample CDK stack for the aws-data-engineering-shenanigans project."""

from typing import Any

from aws_cdk import Stack
from constructs import Construct


class MyStack(Stack):
    """CDK stack (intentionally empty after the sample queue was removed)."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        # CDK forwards stack props dynamically, so Any is required here.
        **kwargs: Any,  # ruff: ignore[any-type]
    ) -> None:
        """Create the (empty) stack."""
        super().__init__(scope, construct_id, **kwargs)
