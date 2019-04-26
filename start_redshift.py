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

def create_redshift_cluster(config, security_group, iam_role):
    """create redshift cluster
    initiates the creation of a redshift cluster created based on the 
    cluster parameters given in the config file 
    and waits till the cluster is up and running.
    Parameters:
    config: config object
    security_group: security group created for redshift to allow external access
    iam_role: iam role created for the redshift cluster
    Returns:
    redshift_cluster: metadata regarding the redshift cluster
    """

    redshift = boto3.client(
        'redshift',
        aws_access_key_id=config.get('AWS_ACCESS', 'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_ACCESS', 'AWS_SECRET_ACCESS_KEY'),
        region_name=config.get('AWS_ACCESS', 'AWS_REGION'), 
    )

    print('Creating Redshift Cluster...')
    response = redshift.create_cluster(
        DBName=config.get('CLUSTER', 'DB_NAME'),
        ClusterIdentifier=config.get('CLUSTER', 'CLUSTER_IDENTIFIER'),
        MasterUsername=config.get('CLUSTER', 'DB_USER'),
        MasterUserPassword=config.get('CLUSTER', 'DB_PASSWORD'),
        # ClusterSecurityGroups=[
        #     security_group['GroupName']
        # ],
        NodeType=config.get('CLUSTER', 'NODE_TYPE'),
        Port=int(config.get('CLUSTER', 'DB_PORT')),
        IamRoles=[
            iam_role['Role']['Arn']
        ],
        NumberOfNodes=int(config.get('CLUSTER', 'NODE_COUNT'))
    )
    print('Redshift Cluster Response.', response)

def main():
    """
    - loads in the config
    - creates iam role
    - creates redshift cluster
    - waits for redshift cluster to be created, and displays details
    """

    config = get_config()
    iam_role = create_iam(config)
    create_redshift_cluster(config, security_group, iam_role)


if __name__ == '__main__':
    main()
