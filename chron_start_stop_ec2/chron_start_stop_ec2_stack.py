from aws_cdk import core
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets

# Make sure to set the Environment Variable Before Running CDK
# run the below code before running #cdk deploy
# export INSTANCE_ID='your-instance-id'
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
                                                        handler="index.handler",
                                                        code=lambda_.InlineCode("""
import boto3
import os

def handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = os.environ['INSTANCE_ID']

    if event['detail-type'] == 'Scheduled Event':
        if 'StartInstance' in event['resources'][0]:
            ec2.start_instances(InstanceIds=[instance_id])
        elif 'StopInstance' in event['resources'][0]:
            ec2.stop_instances(InstanceIds=[instance_id])
                                                        """),
                                                        role=lambda_role,
                                                        environment={
                                                            "INSTANCE_ID": "your-instance-id"  # Replace with your EC2 instance ID
                                                        })

        # Define the CloudWatch Event rules
        start_rule = events.Rule(self, "StartInstanceRule",
                                 schedule=events.Schedule.cron(hour="7", minute="0"))  # 7 AM UTC

        stop_rule = events.Rule(self, "StopInstanceRule",
                                schedule=events.Schedule.cron(hour="18", minute="0"))  # 6 PM UTC

        # Add the Lambda function as the target of the rules
        start_rule.add_target(targets.LambdaFunction(instance_controller_function))
        stop_rule.add_target(targets.LambdaFunction(instance_controller_function))
