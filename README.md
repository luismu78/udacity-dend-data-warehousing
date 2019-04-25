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
* lastName varchar 
* level 
* length double precision
* location varchar 
* page varchar 
* ts integer
* userAgent varchar
* user_id varchar

method, registration, status, and itemInSession were not added, since they are not required for the analytics tables.

**Songs Table**

* artist_id varchar
* artist_latitude double precision
* artist_location varchar 
* artist_longitude double precision
* artist_name varchar 
* duration double precision
* song_id varchar 
* title varchar 
* year integer

With the above considerations, the following schema was selected for the fact, and dimension analytics tables;

#### Fact Table

**songplays** - key distribution

* songplay_id integer NOT NULL PRIMARY KEY
* start_time integer SORT KEY
* user_id varchar DISTKEY FOREIGN KEY REFERENCES users(user_id)
* level varchar
* song_id varchar DISTKEY FOREIGN KEY REFERENCES songs(song_id)
* artist_id varchar FOREIGN KEY REFERENCES artists(artist_id)
* session_id integer SORTKEY
* location varchar 
* user_agent varchar

Key distribution has been chosen for the songplays table, with a distribution key of song_id and user_id. This is because joins will be primarily made between the songplays, and the song and user metadata itself. As well as this, the song and user tables is most likely to grow in size. This selection will also allow the data to be distributed evenly over the nodes, avoiding skew. The user id is chosen as a varchar, since this is how the data is represented in the log data.

We have created foreign keys with the user_id, song_id, and artist_id, as this information will be used for joins. 

We have used the start_time and the session_id as sort keys, since we may need to perform filtering based on these values. 

#### Dimension Tables

**users** - key distribution

* user_id varchar NOT NULL PRIMARY KEY DISTKEY
* first_name varchar
* last_name varchar
* gender varchar
* level varchar

We have chosen the user_id as the distkey, such as to match the fact table. This will help query performance with regards to performing joins on the user_id. 

**songs** - key distribution

* song_id varchar NOT NULL PRIMARY KEY DISTKEY
* title varchar 
* artist_id varchar FOREIGN KEY REFERENCES artists(artist_id)
* year integer SORT KEY
* duration double precision

We have chosen song_id as the distribution key, such as to match the fact table, for query performance. The year is given as a sort key, since filtering may be given on this column. We have added the artist_id as a foreign key reference such as to be able to perform joins with the artist table.

**artists** - all distribution

* artist_id varchar NOT NULL PRIMARY KEY
* name varchar
* location varchar
* latitude double precision
* longitude double precision 

We have chosen an all distribution for this table, since we consider the artists to have slowly changing dimensions, and to not grow too large by redshift standards.

**time** - auto distribution

* start_time integer NOT NULL
* hour integer 
* day integer
* week integer
* month integer 
* year integer 
* weekday integer

We have chosen an 'auto' distribution for the time, since we are not going to be performing many joins on this table, hence we can let redshift distribute the data in an automated way without losing query performance. 


