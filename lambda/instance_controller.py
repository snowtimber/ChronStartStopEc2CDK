import boto3
import os

def handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = os.environ['INSTANCE_ID']

    if 'StartInstance' in event['resources'][0]:
        ec2.start_instances(InstanceIds=[instance_id])
    elif 'StopInstance' in event['resources'][0]:
        ec2.stop_instances(InstanceIds=[instance_id])
