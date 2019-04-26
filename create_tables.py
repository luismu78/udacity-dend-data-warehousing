import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries
from helpers import connect_database

def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    conn = connect_database()
    cur = conn.cursor()
    
    print('Dropping Tables...')
    drop_tables(cur, conn)
    print('Dropped Tables, Creating Tables')
    create_tables(cur, conn)
    print('Created Tables')

    conn.close()


if __name__ == "__main__":
    main()