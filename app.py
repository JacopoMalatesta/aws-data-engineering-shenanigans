"""CDK entrypoint: wires the sample stack to the AWS environment."""

from aws_cdk import App, Environment

from aws_data_engineering_shenanigans.main import MyStack
from constants import AWS_ACCOUNT_ID, AWS_REGION

app = App()
_ = MyStack(
    app,
    "aws-data-engineering-shenanigans-dev",
    env=Environment(account=AWS_ACCOUNT_ID, region=AWS_REGION),
)

_ = app.synth()
