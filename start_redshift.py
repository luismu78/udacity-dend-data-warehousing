"""Start Redshift

Start Redshift will do the following;

- Create an IAM role / policy which is able to read from S3
- Create a redshift cluster based on the provided configuration

"""

import json
import time 
import boto3
import botocore

from helpers import get_config, check_redshift_cluster_status


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
            PolicyArn=config.get('IAM', 'POLICY_ARN')
        )
    except Exception as e:
        raise e
    print('Successfully Created Role, and Attached S3 Read-Only Policy.')
    return role

def create_redshift_cluster(config, iam_role):
    """create redshift cluster
    initiates the creation of a redshift cluster created based on the 
    cluster parameters given in the config file 
    and waits till the cluster is up and running.
    Parameters:
    config: config object
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
    try:
        response = redshift.create_cluster(
            DBName=config.get('CLUSTER', 'DB_NAME'),
            ClusterIdentifier=config.get('CLUSTER', 'CLUSTER_IDENTIFIER'),
            MasterUsername=config.get('CLUSTER', 'DB_USER'),
            MasterUserPassword=config.get('CLUSTER', 'DB_PASSWORD'),
            NodeType=config.get('CLUSTER', 'NODE_TYPE'),
            Port=int(config.get('CLUSTER', 'DB_PORT')),
            IamRoles=[
                iam_role['Role']['Arn']
            ],
            NumberOfNodes=int(config.get('CLUSTER', 'NODE_COUNT'))
        )
        print('Create Cluster Call Made.')
    except Exception as e:
        print('Could not create cluster', e)
        
    cluster_initiated = time.time()
    status_checked = 0
    while True:
        print('Getting Cluster Status..')
        cluster_status = check_redshift_cluster_status(config, redshift)
        status_checked += 1
        if cluster_status['ClusterStatus'] == 'available':
            break
        print('Cluster Status', cluster_status)
        print('Status Checked', status_checked)
        print('Time Since Initiated', time.time() - cluster_initiated)
        time.sleep(5)
    print('Cluster is created and available.')    


def main():
    """
    - loads in the config
    - creates iam role
    - creates redshift cluster
    - waits for redshift cluster to be created, and displays details
    """

    config = get_config()
    iam_role = create_iam(config)
    create_redshift_cluster(config, iam_role)


if __name__ == '__main__':
    main()
