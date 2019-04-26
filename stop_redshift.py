"""Stop Redshift

Stop Redshift will do the following

- Remove the IAM role / policy created for redshift to read from S3
- Remove the Redshift Cluster if it exists.

"""

import time 
import configparser
import boto3
import botocore

from helpers import get_config, check_redshift_cluster_status

def remove_iam(config):
    """remove iam

    remove iam should remove the IAM roles and policies created

    Parameters:
    config: configuration object

    """

    IAM = boto3.client(
        'iam',
        aws_access_key_id=config.get('AWS_ACCESS', 'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_ACCESS', 'AWS_SECRET_ACCESS_KEY'),
        region_name=config.get('AWS_ACCESS', 'AWS_REGION')
    )
    iam_role_name = config.get('IAM_ROLE', 'NAME')
    iam_policy_arn = config.get('IAM_ROLE', 'ARN')

    try:
        IAM.detach_role_policy(
            RoleName=iam_role_name,
            PolicyArn=config.get('IAM_ROLE', 'ARN')
        )
        print('detached role policy')
    except Exception as e:
        print('Could not remove role policy', e)

    try:
        IAM.delete_role(
            RoleName=iam_role_name
        )
        print('removed iam role.')
    except Exception as e:
        print('Could not remove IAM role', e)

def delete_redshift_cluster(config):
    """delete redshift cluster

    delete redshift clsuter should remove the existing redshift cluster

    Parameters:
    config: configuration object

    """
    redshift = boto3.client(
        'redshift',
        aws_access_key_id=config.get('AWS_ACCESS', 'AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config.get('AWS_ACCESS', 'AWS_SECRET_ACCESS_KEY'),
        region_name=config.get('AWS_ACCESS', 'AWS_REGION'), 
    )
    try:
        redshift.delete_cluster(
            ClusterIdentifier=config.get('CLUSTER', 'CLUSTER_IDENTIFIER'),
            SkipFinalClusterSnapshot=True
        )
        print('deleted redshift cluster.')
    except Exception as e:
        print('could not delete redshift cluster', e)

    cluster_delete_actioned = time.time()
    while True:
        cluster_status = check_redshift_cluster_status(config, redshift)
        if cluster_status is None:
            print('Cluster is deleted.')
            break
        print('Cluster is', cluster_status['ClusterStatus'])
        time.sleep(5)
        print('Time since delete actioned', time.time() - cluster_delete_actioned)

def main():
    """main 

    the main function should get the config 
    then, remove the iam role and policy if they exists
    delete the existing redshift cluster.

    """

    config = get_config()
    remove_iam(config)
    delete_redshift_cluster(config)

if __name__ == '__main__':
    main()

