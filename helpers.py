"""Helpers

Helper functions for the data warehousing project.

"""

import configparser

def get_config():
    """
    Loads in the config object from the dwh.cfg file

    Returns
    config: config object from dwh.cfg file
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    return config


def check_redshift_cluster_status(config, redshift):
    """check redshift cluster status
    for a particular redshift cluster, finds the current status of the cluster
    returns false if it is creating, true if running, or None if not initiated
    Paramters:
    config: configuration object
    redshift: redshift boto3 client
    Returns:
    status: status of the created redshift cluster
    """
    try:
        cluster_status = redshift.describe_clusters(
            ClusterIdentifier=config.get('CLUSTER', 'CLUSTER_IDENTIFIER')
        )
    except Exception as e:
        print('could not get cluster status', e)
        return None
    return cluster_status['Clusters'][0]