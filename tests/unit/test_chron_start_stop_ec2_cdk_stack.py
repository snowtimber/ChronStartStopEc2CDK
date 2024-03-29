import aws_cdk as core
import aws_cdk.assertions as assertions

from chron_start_stop_ec2_cdk.chron_start_stop_ec2_cdk_stack import ChronStartStopEc2CdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in chron_start_stop_ec2_cdk/chron_start_stop_ec2_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ChronStartStopEc2CdkStack(app, "chron-start-stop-ec2-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
