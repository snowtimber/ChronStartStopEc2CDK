import os
from aws_cdk import core, aws_iam as iam, aws_lambda as lambda_, aws_events as events, aws_events_targets as targets

class Ec2StartStopStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read the EC2 instance ID from an environment variable
        instance_id = os.environ.get('INSTANCE_ID')
        if not instance_id:
            raise ValueError("Please set the INSTANCE_ID environment variable")

        # Define the IAM role for the Lambda function
        lambda_role = iam.Role(self, "LambdaExecutionRole",
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")])

        lambda_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=["ec2:StartInstances", "ec2:StopInstances"]
        ))

        # Define the Lambda function
        instance_controller_function = lambda_.Function(self, "InstanceControllerFunction",
                                                        runtime=lambda_.Runtime.PYTHON_3_8,
                                                        handler="instance_controller.handler",
                                                        code=lambda_.Code.asset("lambda"),
                                                        role=lambda_role,
                                                        environment={
                                                            "INSTANCE_ID": instance_id
                                                        })

        # Define the CloudWatch Event rules
        start_rule = events.Rule(self, "StartInstanceRule",
                                 schedule=events.Schedule.cron(hour="7", minute="0"), # 7 AM UTC
                                 targets=[targets.LambdaFunction(handler=instance_controller_function)])

        stop_rule = events.Rule(self, "StopInstanceRule",
                                schedule=events.Schedule.cron(hour="18", minute="0"), # 6 PM UTC
                                targets=[targets.LambdaFunction(handler=instance_controller_function)])

app = core.App()
Ec2StartStopStack(app, "Ec2StartStopStack")
app.synth()
