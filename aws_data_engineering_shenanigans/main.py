from aws_cdk import Duration, Stack
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class MyStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The resources that define your stack go here
        queue = sqs.Queue(
            self,
            "SampleQueue",
            visibility_timeout=Duration.seconds(300),
        )
