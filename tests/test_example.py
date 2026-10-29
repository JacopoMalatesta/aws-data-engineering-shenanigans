"""Tests for the sample CDK stack."""

import pytest
from aws_cdk import App
from aws_cdk.assertions import Template

from aws_data_engineering_shenanigans.main import MyStack


@pytest.fixture(scope="module")
def template() -> Template:
    """Synthesize the sample stack once for all tests in this module.

    Returns:
        The synthesized stack template.
    """
    app = App()
    stack = MyStack(app, "my-stack-test")
    return Template.from_stack(stack)


def test_no_buckets_found(template: Template) -> None:
    """The sample stack must not create any S3 buckets."""
    template.resource_count_is("AWS::S3::Bucket", 0)
