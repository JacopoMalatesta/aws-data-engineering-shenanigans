"""Sample CDK stack for the aws-data-engineering-shenanigans project."""

from typing import TypedDict, Unpack

from aws_cdk import (
    Environment,
    IPropertyInjector,
    IStackSynthesizer,
    PermissionsBoundary,
    Stack,
)
from constructs import Construct


class _StackProps(TypedDict, total=False):
    """Subset of CDK Stack props forwarded by MyStack."""

    analytics_reporting: bool | None
    cross_region_references: bool | None
    description: str | None
    env: Environment | dict[str, object] | None
    notification_arns: list[str] | None
    permissions_boundary: PermissionsBoundary | None
    property_injectors: list[IPropertyInjector] | None
    stack_name: str | None
    suppress_template_indentation: bool | None
    synthesizer: IStackSynthesizer | None
    tags: dict[str, str] | None
    termination_protection: bool | None


class MyStack(Stack):
    """CDK stack (intentionally empty after the sample queue was removed)."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Unpack[_StackProps],
    ) -> None:
        """Create the (empty) stack."""
        super().__init__(scope, construct_id, **kwargs)
