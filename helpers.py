"""Helpers

Helper functions for the data warehousing project.

"""

import configparser
import psycopg2

def get_config():
    """
    Loads in the config object from the dwh.cfg file

    Returns
    config: config object from dwh.cfg file
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    return config


def connect_database():
    """connect database

    connect database connects to the redshift database
    Returns:
    conn: database connection.

    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    HOST = config.get('CLUSTER', 'HOST')
    DB_NAME = config.get('CLUSTER', 'DB_NAME')
    DB_USER = config.get('CLUSTER', 'DB_USER')
    DB_PASSWORD = config.get('CLUSTER', 'DB_PASSWORD')
    DB_PORT = config.get('CLUSTER', 'DB_PORT')
    CONNECTION_STRING = "host={} dbname={} user={} password={} port={}".format(
        HOST,
        DB_NAME, 
        DB_USER, 
        DB_PASSWORD, 
        DB_PORT,
    )
    print('Connecting to RedShift', CONNECTION_STRING)
    conn = psycopg2.connect(CONNECTION_STRING)
    print('Connected to Redshift')
    return conn


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