import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events(
    artist varchar 
    auth varchar
    firstName varchar
    gender varchar
    lastName varchar
    length double precision
    location varchar
    page varchar
    ts integer
    userAgent varchar
    user_id varchar
)
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs(
    artist_id varchar 
    artist_latitude double precision
    artist_location varchar
    artist_longitude double precision
    artist_name varchar
    duration double precision
    song_id varchar
    title varchar
    year integer
)
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplays (
    songplay_id integer NOT NULL PRIMARY KEY
    start_time integer SORKEY
    user_id varchar DISTKEY FOREIGN KEY REFERENCES users(user_id)
    level varchar 
    song_id varchar DISTKEY FOREIGN KEY REFERENCES songs(song_id)
    artist_id varchar FOREIGN KEY REFERENCES artists(artist_id)
    session_id integer SORTKEY
    location varchar
    user_agent varchar
)
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS users(
    user_id varchar NOT NULL PRIMARY KEY DISTKEY
    first_name varchar
    last_name varchar
    gender varchar
    level varchar
)
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS songs(
    song_id varchar NOT NULL PRIMARY KEY DISTKEY
    title varchar
    artist_id varchar FOREIGN KEY REFERENCES artists(artist_id)
    year integer SORT KEY
    duration double precision
)
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artists(
    artist_id varchar NOT NULL PRIMARY KEY
    name varchar
    location varchar
    latitude double precision
    longitude double precision
)
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time(
    start_time integer NOT NULL
    hour integer
    day integer
    week integer
    month integer
    year integer
    weekday integer
)
""")

# STAGING TABLES

staging_events_copy = ("""
""").format()

staging_songs_copy = ("""
""").format()

# FINAL TABLES

songplay_table_insert = ("""
""")

user_table_insert = ("""
""")

song_table_insert = ("""
""")

artist_table_insert = ("""
""")

time_table_insert = ("""
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
