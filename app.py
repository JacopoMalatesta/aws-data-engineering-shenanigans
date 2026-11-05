"""CDK entrypoint: wires the CDK stacks to every configured AWS environment."""

from aws_cdk import Acknowledgment, App, Environment, Validations
from cdk_nag import AwsSolutionsChecks, NIST80053R5Checks

from aws_data_engineering_shenanigans.main import MyStack
from projen_config import DEPLOYMENT_ENVIRONMENTS

app = App()
validations = Validations.of(app)
validations.add_plugins(
    AwsSolutionsChecks(app, verbose=True),
    NIST80053R5Checks(app, verbose=True),
)
# MyStack is intentionally empty while scaffolding, so CDK's built-in
# validation raises CloudFormation-Validate::F0001 (non-empty Resources
# section). Acknowledged to allow strict synthesis from day one; remove this
# acknowledgment when the first real resource is added.
validations.acknowledge(
    Acknowledgment(
        id="CloudFormation-Validate::F0001",
        reason=(
            "MyStack is intentionally empty during scaffolding; remove this "
            "acknowledgment when the first resource is added."
        ),
    ),
)
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
