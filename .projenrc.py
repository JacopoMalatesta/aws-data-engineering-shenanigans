from projen.awscdk import AwsCdkPythonApp

project = AwsCdkPythonApp(
    author_email="jacopomalatesta95@gmail.com",
    author_name="JacopoMalatesta",
    cdk_version="2.189.1",
    module_name="aws_data_engineering_shenanigans",
    name="aws-data-engineering-shenanigans",
    uv=True,
    version="0.1.0",
)

project.synth()