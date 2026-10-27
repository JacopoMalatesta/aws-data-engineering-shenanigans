"""Sample CDK stack for the aws-data-engineering-shenanigans project."""

from typing import Any

from aws_cdk import Duration, Stack
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class MyStack(Stack):
    """CDK stack containing the sample resources."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        # CDK forwards stack props dynamically, so Any is required here.
        **kwargs: Any,  # ruff: ignore[any-type]
    ) -> None:
        """Create the stack and its sample resources."""
        super().__init__(scope, construct_id, **kwargs)

        sqs.Queue(
            self,
            "SampleQueue",
            visibility_timeout=Duration.seconds(300),
        )
