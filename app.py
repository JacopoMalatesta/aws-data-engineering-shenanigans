"""CDK entrypoint: wires the CDK stacks to every configured AWS environment."""

from aws_cdk import App, Environment

from aws_data_engineering_shenanigans.main import MyStack
from projen_config import DEPLOYMENT_ENVIRONMENTS

app = App()
for deployment_environment in DEPLOYMENT_ENVIRONMENTS:
    environment_name = deployment_environment["environment_name"]
    _ = MyStack(
        app,
        f"aws-data-engineering-shenanigans-{environment_name.value}",
        env=Environment(
            account=deployment_environment["aws_account_id"],
            region=deployment_environment["region_name"],
        ),
    )

_ = app.synth()
