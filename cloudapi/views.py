from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import boto3
from botocore.exceptions import ClientError

@api_view(['POST'])
def set_aws_creds(request):
    access_key = request.data.get('access_key')
    secret_key = request.data.get('secret_key')
    region = request.data.get('region', 'us-east-1')  # default region

    if not access_key or not secret_key:
        return Response({'error': 'Missing AWS credentials.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Try to call sts.get_caller_identity to validate credentials
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()

        return Response({
            'message': 'Credentials are valid.',
            'user_arn': identity['Arn'],
            'user_id': identity['UserId'],
            'account': identity['Account']
        })

    except ClientError as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])  # Using POST since the request will send AWS credentials
def get_permissions(request):
    # Extract AWS credentials from the request body
    access_key = request.data.get('aws_access_key_id')
    secret_key = request.data.get('aws_secret_access_key')
    session_token = request.data.get('aws_session_token')  # Optional, if using temporary credentials

    # Validate that access and secret keys are provided
    if not access_key or not secret_key:
        return Response({'error': 'Missing AWS credentials (Access Key ID and Secret Access Key are required)'}, status=400)

    try:
        # Initialize a session using the provided AWS credentials
        aws_session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,  # Optional if temporary credentials are used
            region_name='us-east-1'  # Adjust region if necessary
        )

        # Create an STS client to get the identity of the caller
        sts = aws_session.client('sts')
        user_arn = sts.get_caller_identity()['Arn']

        # Create an IAM client
        iam = aws_session.client('iam')

        # A small sample of actions, can be expanded
        actions = [
            'ec2:DescribeInstances',
            'ec2:RunInstances',
            'ec2:TerminateInstances',
            'iam:ListUsers',
            's3:ListBucket',
            'cloudwatch:PutMetricData'
        ]

        # Simulate the policy for these actions
        result = iam.simulate_principal_policy(
            PolicySourceArn=user_arn,
            ActionNames=actions
        )

        # Collect allowed actions
        allowed_actions = [
            r['EvalActionName']
            for r in result['EvaluationResults']
            if r['EvalDecision'] == 'allowed'
        ]

        # Return the result
        return Response({'user_arn': user_arn, 'allowed_actions': allowed_actions})

    except Exception as e:
        return Response({'error': str(e)}, status=500)

