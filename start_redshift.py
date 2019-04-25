"""Start Redshift

Start Redshift will do the following;

- Create an IAM role / policy which is able to read from S3
- Create a Security Group whereby the redshift cluster can be accessed on the given port
- Create a redshift cluster based on the provided configuration

"""

import json
import configparser
import boto3
import botocore


def get_config():
    """
    Loads in the config object from the dwh.cfg file

    Returns
    config: config object from dwh.cfg file
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    return config


def create_iam(config):
    """
    Create IAM creates the neccessary iam role and policy to be able to read from S3

    Parameters:
    config: config object from the dwh.cfg file
    Returns:
    role: created role attached to the redshift cluster.
    """
    IAM = boto3.client(
        'iam',
        aws_access_key_id=config.get('AWS_ACCESS', 'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_ACCESS', 'AWS_SECRET_ACCESS_KEY'),
        region_name=config.get('AWS_ACCESS', 'AWS_REGION')
    )
    iam_role_name = config.get('IAM_ROLE', 'NAME')

    # role = None
    try:
        role = IAM.create_role(
            RoleName=iam_role_name,
            Description='Allows Redshift to Access Other AWS Services',
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "redshift.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
        )
        print('IAM Role Arn:', role['Role']['Arn'])
    except IAM.exceptions.EntityAlreadyExistsException:
        print('IAM role already exists.')
        role = IAM.get_role(RoleName=iam_role_name)
        print('IAM Role Arn:', role['Role']['Arn'])

    try:
        IAM.attach_role_policy(
            RoleName=iam_role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
        )
    except Exception as e:
        raise e
    print('Successfully Created Role, and Attached S3 Read-Only Policy.')
    return role


def create_security_group(config):
    """
    creates the security group such the redshift cluster can be accessed on the 
    neccessary port, and subsequently authorizes the security group such that 
    it exposes the required port

    Arguments:
    config: configuration object, loaded in from dwh.cfg
    Returns:
    security_group: security group metadata from the created security group.
    """

    EC2 = boto3.client(
        'ec2',
        aws_access_key_id=config.get('AWS_ACCESS', 'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_ACCESS', 'AWS_SECRET_ACCESS_KEY'),
        region_name=config.get('AWS_ACCESS', 'AWS_REGION')
    )

    try:
        security_group = EC2.create_security_group(
            Description='Security Group to Allow External Access to Redshift',
            GroupName=config.get('CLUSTER', 'SECURITY_GROUP_NAME'),
        )
    except botocore.exceptions.ClientError as e:
        print('Handling Create Security Group Err:', e)
        security_group = EC2.describe_security_groups(
            GroupNames=[
                config.get('CLUSTER', 'SECURITY_GROUP_NAME')
            ]
        )['SecurityGroups'][0]

    try:
        EC2.authorize_security_group_ingress(
            GroupName=config.get('CLUSTER', 'SECURITY_GROUP_NAME'),
            CidrIp='0.0.0.0/0',
            IpProtocol='TCP',
            FromPort=int(config.get('CLUSTER', 'DB_PORT')),
            ToPort=int(config.get('CLUSTER', 'DB_PORT'))
        )
    except botocore.exceptions.ClientError as e: 
        print('Handling Authorize Security Group Err:', e)
    
    print('Security Group Created, and security group authorized:', security_group)


def main():
    """
    - loads in the config
    - creates iam role
    - creates security group
    - creates redshift cluster
    - waits for redshift cluster to be created, and displays details
    """

    config = get_config()
    iam_role = create_iam(config)
    security_group = create_security_group(config)


if __name__ == '__main__':
    main()
