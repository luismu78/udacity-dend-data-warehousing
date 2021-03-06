## Udacity Data Warehousing Project

A music streaming startup, 'Sparkify', currently has JSON logs for user activity, as well as JSON metadata for songs in the application. These JSON documents currently reside in S3. 

The aim of the project is to build an ETL pipeline, which will extract the data from S3, stage the data in redshift, and subsequently transform the data into a set of dimension tables in redshift, which can then be used for analysis of application usage. 

From an analytics perspective, the 'Sparkify' team wishes to be able to find insights into which songs their users are listening to.

### Redshift Considerations

The schema design in redshift can heavily influence the query performance associated. Some relevant areas for query performance are;

* Defining how redshift distributes data across nodes. 
* Defining the sort keys, which can determine ordering and speed up joins.
* Definining foreign key and primarty key constraints.

#### Data Distribution

How data is distributed is orchestrated by the selected distribution style. When using a 'KEY' distribution style, we inform redshift on how the data should be distributed across nodes, as data will be distributed such that data with that particular key are allocated to the same node. 

A good selection for this distribution keys is such that data is distributed evenly, such as to prevent performance hotspots, with collocating related data such that we can easily perform joins. We essentially want to perform joins on columns which are a distribution key for both the tables. Then, redshift can run joins locally instead of having to perform network I/O. We want to choose one dimension table to use as the distribution key for a fact table when using a star schema. We want to use the dimension table which is most commonly joined.

For a slowly changing dimension table, of relatively small size (<1M entries in the case of Redshift) using an 'ALL' distribution style is a good choice. This distributes the table across all nodes for each of retrieval and performance. 

#### Data Ordering

Using a 'sort key' determines the order with which data is stored on disk for a particular table. Query Performance is increased when the sort key is used in the where clause. Only one sort key can be specified, with multiple columns. Using a 'Compound Key', specifies precedence in columns, and sorts by the first key, then the second key. 'Interleaved Keys', treat each column with equal importance. Compound keys can improve the performance of joins, group by, and order by statements. 

#### Primary & Foreign Key Constraints

We can declare primary key and foreign key relationships between dimensions and fact tables for star schemas. Redshift uses this information to optimize queries, by eliminating redundant joins. We must ensure that primary key constraints are enforced, with no duplicate inserts.

### Schema Selection

The following schema has been selected for the staging tables;

**Events Table**

* artist varchar
* auth varchar
* firstName varchar 
* gender varchar 
* itemInSession integer
* lastName varchar 
* length double precision
* level varchar
* location varchar 
* method varchar
* page varchar 
* registration double precision
* sessionId integer
* song varchar
* status integer
* ts bigint
* userAgent varchar
* user_id varchar

**Songs Table**

* artist_id varchar
* artist_latitude double precision
* artist_location varchar 
* artist_longitude double precision
* artist_name varchar 
* duration double precision
* num_songs integer
* song_id varchar 
* title varchar 
* year integer

With the above considerations, the following schema was selected for the fact, and dimension analytics tables;

#### Fact Table

**songplays** - key distribution

* songplay_id integer NOT NULL PRIMARY KEY
* start_time timestamp NOT NULL SORT KEY
* user_id varchar NOT NULL FOREIGN KEY REFERENCES users(user_id)
* level varchar
* song_id varchar DISTKEY FOREIGN KEY REFERENCES songs(song_id)
* artist_id varchar FOREIGN KEY REFERENCES artists(artist_id)
* session_id integer SORTKEY
* location varchar 
* user_agent varchar

Key distribution has been chosen for the songplays table, with a distribution key of song_id. This is because joins will be primarily made between the songplays, and the song  metadata itself. As well as this, the song table is most likely to grow in size. This selection will also allow the data to be distributed evenly over the nodes, avoiding skew. The user id is chosen as a varchar, since this is how the data is represented in the log data. For each songplay, the start time, and user id must be not null, and hence these restrictions have been reflected in the schema.

We have created foreign keys with the user_id, song_id, and artist_id, as this information will be used for joins. 

We have used the start_time and the session_id as sort keys, since we may need to perform filtering based on these values. 

#### Dimension Tables

**users** - all distribution

* user_id varchar NOT NULL PRIMARY KEY
* first_name varchar
* last_name varchar
* gender varchar
* level varchar NOT NULL

We have chosen an all distribution for this table, since we will have to make joins with the users from the songplays table. We consider that the users will have slowly changing dimensions with regards to the songs, and will not grow too large with regards to redshift standards. The level of the user should not be nullable, and hence we added a not null constraint.

**songs** - key distribution

* song_id varchar NOT NULL PRIMARY KEY DISTKEY
* title varchar 
* artist_id varchar FOREIGN KEY REFERENCES artists(artist_id) NOT NULL
* year integer SORT KEY
* duration double precision

We have chosen song_id as the distribution key, such as to match the fact table, for query performance. The year is given as a sort key, since filtering may be given on this column. We have added the artist_id as a foreign key reference such as to be able to perform joins with the artist table. The artist id should always exist, and hence we added a NOT NULL constraint on this column.

**artists** - all distribution

* artist_id varchar NOT NULL PRIMARY KEY
* name varchar NOT NULL
* location varchar
* latitude double precision
* longitude double precision 

We have chosen an all distribution for this table, since we consider the artists to have slowly changing dimensions, and to not grow too large by redshift standards. The artist should always have an accompanying name, and hence we added a not null constraint to this.

**time** - auto distribution

* start_time integer NOT NULL PRIMARY KEY
* hour integer 
* day integer
* week integer
* month integer 
* year integer 
* weekday integer

We have chosen an 'auto' distribution for the time, since we are not going to be performing many joins on this table, hence we can let redshift distribute the data in an automated way without losing query performance. The start time is given as the primary key for the table.

### Project Requirements

The requirements for the project are a valid aws account, with accompanying security credentials, as well as a python environment, which satisfies the module requirements given in requirements.txt

You will need to add aws access key and secret information to the dwf.cfg file, under AWS ACCESS. This is not to be comitted to git.

### Redshift

In order to spin up a redshift cluster, we need the following;

* To create an IAM role and policy for the redshift cluster to inherit
* To create the redshift cluster given a particular configuration.

To spin down the redshift cluster, we wish to remove the above mentioned.

To follow IAC (Infrastructure as Code) practices, and to allow us to easily spin up and spin down the redshift cluster to save costs, we can use the following scripts;

* start_redshift.py
* stop_redshift.py

The scripts will create/remove the neccessary resources for redshift to run.

## ETL Pipeline

The ETL pipeline comprises of two steps;

1. Loading the data into the staging tables on redshift from S3.
2. Populating analytics tables in redshift from the staging tables.

In the first step, we wish to copy the data from two directories of JSON formatted documents, staging_events, and staging_songs. For the staging songs, we are provided with the format of the data in 's3://udacity-dend/log_json_path.json' and hence we COPY the staging events using this document as the format. With regards to staging songs, no format is provided, and hence we use the 'auto' format for copying across the data.

With regards to creating the analytics tables, we firstly create the songs table from the staging_songs table, using 'SELECT DISTINCT' statements to avoid duplicates in the songs. We do the same for artists, and users respectively, once again using a 'SELECT DISTINCT' statement to avoid duplication. To create the songplays analytics tables, select from the staging_events table, joining artists and songs tables to retrieve the song_ids and artists_ids. We filter the insert statement by the entries for which page is equal to 'NextSong'. We create the time table from the songplays. we use the 'extract' function, to extract the particular part of the datetime object, and the 'timestamp' function to convert the epoch timestamp to a datetime object. 

The ETL pipeline is such that the script will load all events from the json files into staging tables, and subsequently into analytics tables, such that the sparkify analytics team can produce valuable insights into user listening behaviour.

