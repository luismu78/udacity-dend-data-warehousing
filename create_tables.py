import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
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
    print('Connecting to RedShift on', CONNECTION_STRING)
    conn = psycopg2.connect(CONNECTION_STRING)
    print('Connected to Redshift')
    cur = conn.cursor()
    
    print('Dropping Tables...')
    drop_tables(cur, conn)
    print('Dropped Tables, Creating Tables')
    create_tables(cur, conn)
    print('Created Tables')

    conn.close()


if __name__ == "__main__":
    main()