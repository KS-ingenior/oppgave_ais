Todo:
* Skrive noe mer om oppgave og hensikt i innledningen
* Tydeligere forventning om progresjon i oppgavene, dvs hvor langt bør du ha kommet til gitte tidspunkt. Ambisjonen bør være at de bør være ferdig med all import og prepping av data (index o.l.) slik at dag 2 ogdag 3 kan brukes på analyser.
* Slå sammen dataene til større filer for å gjøre importen enklere. Kikke på HAIS og danske data for å sjekke hvordan dataene er strukturert, og la seg inspirerere av dette.
* Vurdere om det skal være en lett sti og en vanskelig sti, som kan benyttes under data import.
* Legge til mer feilkorreksjon under "clean" av data
* Lage et underkapitel om visulaisering av AIS-data. Ta utgangspunkt i noe som dette kanskje: https://www.youtube.com/watch?v=XSfeKSQ-JG0
* Skrive inn mer av scenario i teksten slik at de får mer hjelp med analysene?
* Lage en backup av databasen som kan gis til de som ikke har kommet så langt som ønsket etter dag 1. Vil gjøre det enklere å følge progresjonen

This assignment is based on ["Maritime Data Processing in Relational Databases"](https://hal.science/hal-03137050) by Etienne et.al [^1]


## 1. Analysing spatial data

The analysis and the processing of data from automated surveillance technologies like the Automatic Identification System (AIS), Synthetic Aperture Radar (SAR), satellite images and coastal radars is an emerging topic. Once fused with contextual information like coastlines, nautical charts, fishing areas, maritime protected areas, sea state and weather conditions, these positioning data can be analysed in order to understand vessel mobility, monitor maritime traffic, uncover activities or risks for the environment, living resources and navigation, and so on. The research is expeditiously progressing, and many analysis techniques are applied to attain the above major goals using maritime navigational data. Some of the leading maritime informatics research topics include:
*	Vessel trajectory analysis and prediction, recently focusing mainly on AIS and complementary sources to predict and analyse vessel trajectories.
*	Traffic forecasting, like port volume handling and cargo throughput forecast.
*	Collision prevention, analysing risk of ships collisions through the analysis of their navigational behaviour.
*	Ship detection, classification and identification, analysing videos from cameras in delimited areas, for instance to detect small vessels, or remote sensing images in larger areas.
*	Anomaly detection, mostly adopting data-driven methods to model normal traffic against which any irregular behaviour is associated to potential threats.
*	Analysis of human activities at sea, such as fishing, illegal traffic (human beings, narcotics, goods), piracy.
*	Multi-source information fusion, to reduce uncertainty in the data available and achieve better accuracy in analysis.
*	Dynamics of maritime transportation networks, where trajectory data are considered at an aggregated level through network abstractions designed to analyse behavioral patterns.


## 2. Systems for spatial data and moving objects
In this section, we overview how spatial, specifically geographic data, and moving objects are handled, either using Geographic Information Systems (GIS), or DBMS. The approaches and software products supporting only spatial data are introduced first, followed by some of the existing systems for spatio-temporal data.

### 2.1 Handling spatial data
For decades, the representation and analysis of geographical information have been investigated in the area of Geographic Information Systems (GIS). GIS, like ArcGIS , GRASS , and QGIS  naturally evolved from the digitalisation of cartographic maps. GIS have efficient geographic visualisation and rendering capabilities, which can be combined with multi-layer spatial analysis functions like distance/buffer and topological queries, overlay operations, surface and terrain analysis. However, traditional GIS alone cannot deal with the increasing quantity of data, and do not suite the semantically-driven integration of heterogeneous information that involves both spatial and non-spatial attributes, or complex knowledge discovery tasks like supervised classification. All these tasks require an integrated representation of geographic and descriptive data features, and a greater flexibility in low-level data manipulation than the one offered by traditional GIS, which keep the management of geospatial data and other data types separated.

To address the needs of emerging spatial-driven applications, relational database systems, once geared towards providing efficient support for simple objects with discrete attributes, have been extended to represent and query geographic data in a natural way. For instance, Oracle  and Postgres (now PostgreSQL), were expanded with spatial modules, respectively Oracle Spatial (now fully integrated in the main DBMS) and PostGIS. Nowadays, all the main DBMS, including Microsoft SQL , MySQL , SQLite  with SpatiaLite, provide support to cope with geographic data.

The data model of these DBMS has been extended with data types and structures for managing geometric data, relying on established international standards and recommendations ,.  Spatial operations and types are fully integrated with the query language, and the DBMS engine is enhanced to map from the query language to the spatial features. Also, spatial indexing is provided for query optimisation. Most of the products include B-Tree+ and R-Tree indexes. PostgreSQL additionally implements the Generalized Search Tree (GiST) [18] to develop customised indexing, mixing, for instance, spatial and non-spatial optimisation.
Most DBMS spatial extensions provide mature support for geometric data. Some products include also extensions for raster data (e.g. Oracle Raster and pgraster, which is integrated in PostGIS). Also, few products support 3D representations, including PostGIS.

This support can be further enhanced with novel abstract data types to represent spatial (and spatio-temporal) data, tailored to the application, analogously to objectoriented DBMS (OODBMS). These (object-) relational DBMS, taking advantage of both spatial and object-oriented functionalities, have been established as main players on the market for storing and querying spatial data. For this reason, nowadays most of GIS enable the use of a spatial DBMS as data storage layer. This hybrid solution combines the advantages of the efficient front-end of GIS and the robust and efficient storage and retrieval capabilities of spatial DBMS.
Few NoSQL, or Not-only-SQL, DBMS, i.e. all the DBMS that adopt alternative models to the (object-)relational one, offer spatial extensions. Among them, few research proposals exist to extend OODBMS to support spatial features, leveraging the model extensibility as described above. More recent NoSQL DBMS, like MongoDB and DocumentDB, which adopt a semi-structured document-based data model, enable the definition of spatial entities supporting GeoJSON objects and geo-spatial queries. ArangoDB is a multi-model (key value, graph and document) NoSQL DBMS that supports natively geo-spatial querying and indexing. Rasdaman (which stays for raster data manager) is a multi-dimensional DBMS for scientific data, which can be queried with an SQL-like language.

NoSQL DBMS relax some data modelling constraints to handle unstructured or semi-structured data, and improve scalability performance as required for big data and parallel processing. For instance, in order to process in parallel multiple vessel trajectories, and multiple areas, they enable to increase, seamlessly for the application, the number of nodes in the infrastructure that are used to host the database, and maintain replicas of the data. However, the gain in efficiency and flexibility comes at the price of relaxing some of the properties that, in traditional SQL databases, guarantee data consistency (namely, ACID properties: i.e. atomicity, consistency, isolation, and durability).
It should be noted that NoSQL solutions do not always outperform relational DBMS. For instance, the authors in compare PostgreSQL/PostGIS and MongoDB performance on a maritime dataset of vessel positions, and show that PostgreSQL/PostGIS outperforms MongoDB. As shown in the Knowledge base of relational and NoSQL DBMS,  relational DBMS remain amongst the most popular DBMS.

## 2. Building a maritime information system
A Maritime Information System can be defined as a system for the collection, processing, storage and delivering of maritime information through a visualisation interface. The main purpose of a DBMS, when integrated to such a Maritime Information System, is to organise, store, access and process the maritime data. The database can be handled and queried through a management tool or an external programming environment (e.g. Python, R, Java). In order to visualise the data, dedicated applications and Application Programming Interface (API), e.g. Grafana,  Data Driven Documents (D3),  Kibana,  visual analytics tools or a GIS software like QGIS can be used.

> [!IMPORTANT]
> ACTION REQUIRED:
> Download and install the following software to prepare the working environment
>* POSTGRESQL with POSTGIS extension (https://www.postgresql.org/download/)
>* PGAdmin (www.pgadmin.org)
>* QGIS (www.qgis.org)


### 3.1 PostgreSQL DBMS
The DBMS employed in this chapter to illustrate the use of relational databases for maritime data is PostgreSQL. PostgreSQL is an open source, standard compliant and robust DBMS. It adopts and extends the Structured Query Language (SQL) for data manipulation and querying. PostgreSQL runs on all major operating systems and can handle big datasets. PostgreSQL is highly extensible: the users can define their own data types, build customised new functions and interact with the DBMS through the query language SQL, using different programming languages like C, Perl, Java, Python, R, JavaScript, etc., and from shell scripts. I do specifically advice you to read the [documentation](https://www.postgresql.org/docs/current/) for troubleshooting and deeper understanding of PostgreSQL and a pretty good intro SQL.

### 3.2 PostGIS spatial extension
The spatial component of the maritime dataset plays a fundamental role for maritime situational awareness. PostGIS is a powerful add-on to PostgreSQL that adds geospatial capabilities to the DBMS. PostGIS integrates both raster and vector types of data which are fully compliant with the OGC Simple Features Specification for SQL, and a large number of spatial operations. PostGIS also implements multiple spatial indexing methods, including R-Tree and GiST. Although PostgreSQL and PostGIS are usually used with two-dimension (2-D) geometries (coordinates X and Y), PostGIS supports the addition of a third dimension (Z), allowing to reason with three-dimensional geometries.

### 3.3 PGAdmin management tool
Once the DBMS is installed, management tools are useful to setup and query the database. pgAdmin is a multi-platform software that is dedicated to manipulate PostgreSQL databases. Once connected to a PostgreSQL cluster (i.e. a collection of PostgreSQL servers), pgAdmin can create and query new databases and tables. Its powerful query tool supports colour syntax highlighting and graphical query plan displaying.

### 3.4 QGIS visualization tool
QGIS is the last component of our Maritime Information System. It is a user-friendly open-source GIS, which can retrieve, manage, display and analyse the geographic data stored in the PostgreSQL/PostGIS database. In this chapter, QGIS will be used to exemplify the visualisation and creation of maps to show the results of the spatial queries (see Figure 1). Interested readers can refer to [Anita Graser’s blog, “Free and Open Source GIS Ramblings”,](https://anitagraser.com/)  for practical illustrations on advanced functionalities for movement data. Moreover, I expect you to read the [QGIS online user guide](https://docs.qgis.org/3.40/en/docs/user_manual/index.html)  to get started with QGIS.


### 3.5 Getting the dataset
#### 3.5.1 Download the dataset
The dataset has to be downloaded [here](https://drive.google.com/file/d/1CEcre79-cX-pWZOajiHudHSAZzqZSFqs/view?usp=share_link). The dataset was downloaded from the [Norwegian Coastal Administration's open data stream.](https://www.kystverket.no/navigasjonstjenester/ais/tilgang-pa-ais-data/) using a Google virtual machine and NiFi.

Contains:
- Static data (ais-status)
- Dynamic data (ais-pos)
- Contextual data (pipelines etc) 


#### 3.5.2 Limitations
This data stream has some limitations:

* Applies to the geographical area within the Norwegian economic zone, the fisheries protection zone around Svalbard, and the protection zone around Jan Mayen.
* Does not show fishing vessels under 15 meters.
* Does not show recreational vessels under 45 meters.

#### 3.5.2 Timeframe
* The data covers the timeperiod from 10 February - 28 March 2023


#### 3.5.3 Coverage of Norwegian AIS data
<img src=https://developer.barentswatch.no/assets/images/OpenAisArea2-c5332d2a6ed8f25fba1b5b064ad72b38.PNG alt="Description" width="300">

## 4. Preparation of the dataset
The dataset that you have recently downloaded is downloaded directly from the [Norwegian open AIS stream](https://www.kystverket.no/sjotransport-og-havn/ais/tilgang-pa-ais-data/). Raw AIS data often contain errors, inconsistencies, and missing values due to transmission issues, human input errors, or system limitations. Cleaning and validating the data before importing it into a geodatabase is crucial for several reasons:

* Data Accuracy: Incorrect or malformed data—such as invalid MMSI numbers, unrealistic positions, or malformed timestamps—can lead to erroneous spatial analyses and misinterpretation of vessel behavior. In addition this will also lead to the import of data into the database will fail.
* Error Prevention: Geodatabases often enforce type constraints; improperly formatted data can cause import failures or corrupt table entries.
* Consistency: Standardizing formats (e.g., timestamps, destination names, ship types) ensures uniformity across datasets, making queries and spatial joins reliable.
* Performance: Large volumes of dirty data can slow down import processes and reduce database performance. Filtering out duplicates or invalid entries improves efficiency.

Cleaning AIS data prior to geodatabase import is essential for ensuring accuracy, reliability, and usability in maritime spatial analyses. Skipping this step risks misleading results and inefficient data management.

## Task 1
- [ ] Open one of the CSV-files in the attached dataset. Then have a look through one of the files and see if you can spot any errors that might lead to errors during import.

In the scripts folder I have prepared a [python-script](scripts/clean_ais.py) that helps you clean the dataset that you have downloaded. This script is designed to clean CSV files containing AIS (Automatic Identification System) data located in a specified folder. The script performs several cleaning operations, including:

* Iterating through all CSV files in the specified folder.
* Removing rows with invalid latitude or longitude values.
* Converting the "speed" column to numeric type, treating non-numeric values as NaN (Not a Number), and setting these NaN values explicitly
* Removing rows with invalid speed values (speeds outside the 0 to 80 range) and invalid course values (courses not between 0 and 359 degrees).
* Saving the cleaned data to a new CSV file, appending _CLEAN to the original filename to distinguish the cleaned dataset.

## 4 Creation of the Database
In this section, a new database will be created and populated. Assuming
that the software packages described in the previou section have been installed, it is possible
to connect to the PostgreSQL database server from pgAdmin interface, using the
credentials provided during the installation. Once a connection to the database is
established, the following command can be executed (in menu Tools -> Query Tool)
to create a new empty database called `INGOF3205`.

```sql
CREATE DATABASE "INGOF3205" ;
```

> [!TIP]
PostgreSQL automatically converts to lower case all tables and fields names. If you want to force
the use of capitals in tables or fields names, you must quote them (i.e. ‘‘tableName’’ or
‘‘fieldName’’). To distinguish field names and strings in queries, PostgreSQL uses double
quotes (‘‘ and ’’) for field names and single quotes (‘ and ’) for string values.


### 4.1 The database schema and the tables
A database is organised and structured using one or more database schemas and several tables. Each schema defines a workspace where new data types, functions and operators can be defined. Organising a database using different schemas is useful for various reasons:
* To organise database objects within logical groups and to ease their management;
* To isolate third-party applications and allow for duplicate objects or function names in different schemas;
* To grant users (and groups of users) appropriate access to data and functions that belong to different schemas.

#### 4.1.2 Schema and tables for AIS data
AIS transceivers on board of vessels broadcast vessel positions and interesting information about static ship characteristics such as the vessel name, callsign (i.e. unique vessel identifier for radio broadcasts), IMO number and ship type. Each AIS transceiver has its own Maritime Mobile Service Identity (MMSI), which is registered and attributed by country of flag. This number identifies the source of the AIS message (`sourcemmsi`). Usually, AIS transceivers broadcast this information to all the ships in the vicinity.  
For the examples presented in this chapter, AIS information will be organised within a schema named `ais_data`. The SQL instructions below show how to create the schema `ais_data` into the database and create, inside this schema, a new table `ais_data.staticships` to store voyage and nominative pieces of information. Note that each attribute has a specific type (integer, text, double, etc.).

```sql
CREATE SCHEMA "ais_data" ;
```

```sql
CREATE TABLE ais_data.static_ships(
  sourcemmsi integer,         -- MMSI number, unique identifier of the vessel's AIS transceiver
  type integer,               -- AIS message type (e.g., 5 for static vessel data)
  imo integer,                 -- IMO number, the vessel's international identification number
  callsign text,              -- Callsign of the vessel
  shipname text,              -- Name of the vessel as reported
  shiptype integer,           -- Numeric ship type code according to AIS standards
  shiptype_text text,         -- Textual description of the ship type
  eta text,                   -- Estimated Time of Arrival as reported by the vessel
  destination text,           -- Destination as reported by the vessel
  timestamp_utc timestamptz,  -- UTC timestamp when the AIS message was received
  id bigserial,               -- Auto-generated unique identifier for the row
  CONSTRAINT static_ships_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
```

### 4.2 Loading the data into the database
The new table can now be populated. Data can be manually inserted into the existing tables using the SQL statement INSERT INTO or, alternatively, directly from files using the PostgreSQL command COPY FROM. The following example shows how to load into the table ´aid_data.staticship´ the static ship information stored in the Comma Separated Values (CSV) stored in the folder named `ais-status`. Her the files area on dates, which is included in the downloaded dataset. In the command below,

> [!TIP]
If you need to be a bit more effective, use this [Python-script](scripts/import_AIS_postgres.py) to help you import all files into the database.

```sql
COPY ais_data.static_ships (
    sourcemmsi,
    type,
    imo,
    callsign,
    shipname,
    shiptype,
    shiptype_text,
    eta,
    destination,
    timestamp_utc
)
FROM '<path to dataset>'
DELIMITER ','
CSV HEADER;
```


As soon as the database table is filled with static data, it can be queried using SQL commands. The query in the next example counts how many different ship names are listed in the table `ais_data.static_ships`. Note the time spent on the query.

```sql
SELECT DISTINCT shipname
FROM ais_data.static_ships;
```

### 4.X Make it faster

```sql
CREATE INDEX idx_static_ships_mmsi ON ais_data.static_ships USING btree (sourcemmsi);
```

### 4.3 Integrating contextual data - Vurder å flytte denne delen lenger ned slik at de får startet med det tidkrevende arbeidet tidlig
The dataset also contain complementary data like the location of the Norwegian armed forces, oil and gas pipeline, other relevant oil infrastructure, submarine cables, a list of suspicious vessel etc. These data have a different nature than AIS data, which are continuously streamed, and provide information useful to contextualise and understand the vessel movements. Conveniently, a dedicated database schema, with name 'context_data', can be created for these data.

## Task 2
- [ ] Create a new schema `context_data` in the database

All contextual (geographic) data in the dataset are in different formats, geopackage, json, csv and others which is well-known formats that is easily read by QGIS. Simply add the data to QGIS and use the `Database Manager` to add the data to the database using the `Import Layer/File`. Verify the tables by looking at column and what type of data that is stored in the different columns before continuing. e.g if a column only contains `INTEGER` but is added to the database as `VARCHAR`, then use the `UPDATE`-function to alter the datatype stored in the different columns.

From the dataset, select the following files and load them in the database maritime informatics as explained above:
* Forsvarets_lokasjoner;
* cabel_geo;
* Oil Refineries
* Oil pipeline

* In addition download the last updated [EU SANCTION DESIGNATED VESSELS](https://www.dma.dk/growth-and-framework-conditions/maritime-sanctions/sanctions-against-russia-and-belarus/eu-vessel-designations) and add the data to the database.

> [!WARNING]
Before continuing, review the different projections (CRS) you have in your database. To use the spatial queries (chapter 5) all data has to be either in geographic or a projected reference system.

```sql
ALTER TABLE context_data.oil_gas_infrastructure ADD COLUMN geom_geo geometry(Point, 4326);

UPDATE context_data.oil_gas_infrastructure
SET geom_geo = ST_Transform(geom, 4326)
WHERE geom IS NOT NULL;

```


### 4.4 Adding Maritime identification digits/country code
[Maritime identification digits](https://en.wikipedia.org/wiki/Maritime_identification_digits) are used by radio communication facilities to identify their home country or base area in digital selective calling (DSC), Automatic Transmitter Identification System (ATIS), and Automatic identification system (AIS) messages as part of their Maritime Mobile Service Identities (MMSI). [The International Telecommunication Union](https://www.itu.int/en/ITU-R/terrestrial/fmd/pages/mid.aspx) facilitates the assignment of MIDs to countries. Note that not all countries have MIDs; those without are typically landlocked, with no access to international waters. Sorting MID assignments in numerical order reveals a regional structure, with the first digit. 

2 assigned to Europe, 3 to North America and the Caribbean, 4 to Asia (except the southeast), 5 to the Pacific and Eastern Indian Oceans and Southeast Asia, 6 to Africa, the Atlantic Ocean and Western Indian Ocean, and 7 to South America.

#### 4.4.1 Creating a lookup table
The following query creates a lookup table that maps a 3-digit Maritime Mobile Service Identity (MMSI) prefix to a country name.
Each MMSI number starts with a prefix that identifies the vessel’s country of registration. This table stores MMSI country prefixes.
```sql
CREATE TABLE context_data.cnty_codes (
    digit INTEGER PRIMARY KEY,
    country VARCHAR(255)
);
```

* digit stores the 3-digit country prefix (e.g., 257-259 = Norway).
* country stores the corresponding country name.
* Making digit the primary key ensures each prefix appears only once.

Copy the data from the CSV-file into the database. 

```sql
COPY context_data.cnty_codes (digit, country)
FROM '<path-to-file>/AIS-country-codes.csv'
DELIMITER ';'
CSV HEADER;
```

> [!TIP]
You may also use the Database Manager tool in QGIS to import the data into the table without using a SQL-statement. This tool can also create tables for you, however it usually treats most values as VARCHAR, meaning you have to redefine the column types later by using an `UPDATE`-statement


#### 4.4.2 Adding Country Information to Ship Data
In the view below we combine the table and get all the data in one. 

### 4.5 Creating a view
The table `ais_data.static_ships` contains duplicated information about ships, transmitted at different timestamps, because nominative messages (ITU 5, ITU 19, and ITU 24) are automatically repeated at regular time intervals. The duplicated rows in this table can be grouped together using a SQL view, as shown in the following example.

```sql
CREATE VIEW ais_data.ships AS
WITH ships AS (
         SELECT static_ships.callsign,
            static_ships.imo,
            static_ships.sourcemmsi,
            static_ships.shipname,
            static_ships.shiptype,
            static_ships.shiptype_text,
            SUBSTRING(static_ships.sourcemmsi::text FROM 1 FOR 3)::integer AS mmsi_prefix
           FROM ais_data.static_ships
        )
 SELECT DISTINCT ON (s.sourcemmsi, s.imo, s.shiptype) s.sourcemmsi,
    s.imo,
    s.shiptype,
    s.callsign,
    s.shipname,
    s.shiptype_text,
    c.country AS cnty,
    c.digit AS cnty_code
   FROM ships s
     LEFT JOIN context_data.cnty_codes c ON s.mmsi_prefix = c.digit;

```
Using the `SELECT DISTINCT` function returns only unique (distinct) rows from the result set of a query. It eliminates duplicate rows, ensuring each row in the output is unique.by all columns essentially removes duplicates. 

## Task 3!
Using the view `ais_data.ships`, let´s assess some quality aspects of the static AIS information, as proposed in the following exercise.
- [ ] How many ships have null, empty or space filled shipname?
- [ ] How many MMSI numbers are used more than once?


> [!TIP]
A table is a database object that stores data physically on disk in rows and columns. It is the primary structure for holding persistent data that can be queried, inserted into, updated, or deleted.
A view is a virtual table defined by a SQL query. It does not store data physically but instead presents a dynamic result set based on the underlying tables. When you query a view, the database executes the underlying query in real time. Views are useful for simplifying complex queries, enforcing security, or presenting data in a specific format.
A materialized view is similar to a view, but it stores the query result physically on disk. This allows for faster access because the data is precomputed, but it must be refreshed periodically to stay up to date with the underlying tables. Materialized views are useful when queries are complex or expensive to compute repeatedly.

### 4.6 Adding movement data
The view `ais_data.ships` and the queries proposed above show that the static ship information is not always accurate, because both fields shipname and sourcemmsi have duplicates and null or empty values. Indeed, this information can be manually modified. Being unreliable and inconsistent, none of these fields can used as a primary key in our tables.

In order to analyse the movement of ships, it is necessary to load their positions in the database. In the maritime dataset, vessel positions are stored in the folder `ais-pos`.

## Task 4!
- [ ] Within the schema `ais_data`, create a new table named `dynamic_ships`. Fill it with the data of the folder `ais-pos`

```sql
-- Create table that contains the moving data
CREATE TABLE ais_data.dynamic_ships(
  course double precision,
  datetime timestamp,
  heading integer,
  lat double precision,
  lon double precision,
  mmsi integer,
  speed double precision,
  status_text text,
  turn text,
  type integer,
  id bigserial,
  CONSTRAINT dynamic_ships_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
```

The following query counts the number of the ships positions contained in the
table `dynamic_ships`

```sql
SELECT COUNT(*) FROM ais_data.dynamic_ships;
```



### 4.7 Make it faster
The queries of the previous section may take a while to complete. This is due to the
size of the table dynamic ships and because the table needs to be fully scanned
for reading and sorting every timestamp in order to execute the queries. Querying
very large tables can take a long time to execute. In order to optimise the queries,
especially if they are executed frequently, the PostgreSQL commands EXPLAIN
and ANALYZE can be used to understand how the DBMS plans to execute them. For
example, the following command asks the PostgreSQL planner what is the execution
plan for the last query in the previous section.

```sql
EXPLAIN ANALYZE SELECT min (timestamp_utc) , max (timestamp_utc) FROM ais_data.dynamic_ships ;
```
In the answer, the PostgreSQL planner indicates that it would perform a sequential
scan (Seq Scan) of the table. The sequential scan can be avoided if the column
t, which appears in the SELECT clause of the query, is previously sorted and
indexed. Indexes can require time to build up, and use storage space on the PostgreSQL
server, but they can drastically decrease the time required to execute a query.
In the SQL example below, a Binary Tree (BTREE) index is created on column `timestamp_utc`.
This index is particularly efficient for reading attributes whose values have a linear
ordering like temporal, numerical or string attributes.


```sql
-- create index on the time column
CREATE INDEX idx_dynamic_ships_time
ON ais_data.dynamic_ships 
USING btree (timestamp_utc) ;
```
> [!TIP]
In order to optimise the queries on very large tables, do not forget to define indexes on the
columns that are often queried.

## Task 5!
- [ ] Find how many different ships have broadcasted their positions on AIS on February 28 2023 and display their ship names. Which tables are required to answer this question? Do you require indexes on these tables?

### 4.8 Make it geographic 
The geo-spatial component is an important feature of the maritime dataset. Ships
move in a specific spatial context made of coastlines, straights, ports, mooring areas,
restricted areas and bathymetry. This information should be considered when
analysing the maritime situation. In order to support this variety of geographic objects,
PostgreSQL can be extended with PostGIS that adds geographic types, functions
and indexes to the DBMS. In order to activate the PostGIS extension on a
PostgreSQL database, it is sufficient to execute the command below.

```sql
CREATE EXTENSION postgis ;
```

A way to represent spatial objects, such as moving vessels, is to use simple geometric features such as points, lines and polygons along with extra alpha-numerical attributes, e.g. the name of the spatial features. This way of modelling spatial objects is called vector representation. The coordinates of spatial objects are expressed in a given Coordinate Reference System (CRS). Thanks to PostGIS, PostgreSQL can handle the following geometric data types:
* POINT, defined using spatial coordinates in a CRS;
* LINESTRING, ordered set of POINTs;
* POLYGON, defined based on a collection of rings, at least one outer and possibly inner rings (representing, e.g. enclaves in countries, reservoirs), given as LINESTRINGs;
* MULTIPOINT, MULTILINESTRING, MULTIPOLYGON, i.e. sets of geometric objects of the same base type;
* GEOMETRYCOLLECTION, a set of geometric objects of various nature.

In the table `dynamic_ships`, vessel positions are given by their coordinates, i.e. longitude and latitude, specified in two separated columns, lon and lat, respectively.
The PostGIS function `ST_MakePoint` creates a POINT from two coordinates, given their CRS. In the example below, the World Geodesic System 1984 (WGS84) is used. It is identified in PostGIS through its Spatial Reference Identifier (SRID) as defined by the European Petroleum Survey Group (EPSG:432620). The World Geodetic System 1984 is extensively used to define worldwide locations by longitude and latitude. This CRS is used by the GPS satellite navigation system integrated into AIS transceivers. The PostGIS function `ST_SetSRID` is used to specify
the CRS’ SRID of the newly created column. As the table `dynamic_ships` has 47 million positions, the update process may take a while (about 20-30 minutes).

```sql
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom geometry(Point,4326);
UPDATE ais_data.dynamic_ships
SET geom=ST_SetSRID (ST_MakePoint(lon,lat),4326) ;

CREATE INDEX idx_dynamic_ships_geom
ON ais_data.dynamic_ships
USING GiST (geom);

CREATE INDEX idx_dynamic_ships_mmsi
ON ais_data.dynamic_ships
USING btree (mmsi) ;

CREATE INDEX idx_dynamic_ships_mmsi_t ON ais_data.dynamic_ships USING btree (mmsi,datetime);
```

The database must be aware of the data’s CRS before executing the commands in the example above. Data’s CRS must be listed in the system table
`spatial_ref_sys`, which is included in the PostgreSQL database public schema. The public schema is automatically created in every PostgreSQL database and contains system tables and functions. It is also used to store all the user-defined tables that are created without referring to any specific schema.

PostGIS can project geometric objects from one CRS to another. In the example below, the function `ST_Transform` is used to project vessel positions expressed in WGS84 into the projection ETRS89/LAEA Europe CRS (EPSG:3035). 

```sql
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom3035 geometry(Point ,3035);

--Copy data from geom and transform them into 3035
UPDATE ais_data.dynamic_ships
SET geom3035 = ST_Transform(geom, 3035)
WHERE geom IS NOT NULL;
```

#### 4.9 Create a table/view with all russian vessels
```sql
CREATE TABLE ais_data.russian_vessels AS
SELECT d.*
FROM ais_data.dynamic_ships d
JOIN ais_data.ships s ON d.mmsi = s.sourcemmsi
WHERE s.cnty_code = 273;
```


##Task 6
- [ ] Create a table or a materialzed view which contains all the vessels in the so called "Shadow Fleet", and included in your database. Write a couple of sentences explaining your decision.
- [ ] 
> [!TIP]
To create this table or materialized view you have to combine `context_data.eudesignated` (for IMO numbers), `ais_data.ships` (for IMO-to-MMSI mapping), and `ais_data.dynamic_ships` (for movement data)

### 5 Spatial queries
Spatial queries evaluate the relationships that hold among objects’ geometries. PostGIS supports the 8 region connection calculus (RCC8) and the Dimensionally Extended nine-Intersection Model (DE-9IM), and complies with the OGC Simple Feature Access ([20]), which defines the supported routines to test spatial relationships between two geometric objects. PostGIS functions that output a value, either a distance (i.e. ST Distance) or a Boolean value (all the others) are shown in Figure 4. PostGIS functions that output a geometry are shown in Figure 5. All functions can be applied between geometries of various types (i.e. POINTS,LINESTRINGS or POLYGONS), as far as the coordinates of these objects are defined in the same CRS. These spatial relationship functions can be combined with temporal operators, enabling to express complex spatio-temporal queries.

<img width="400" alt="Figure 4" src="https://github.com/user-attachments/assets/289e5915-faa0-4738-bc35-4051cd0ef141" />

The functions `ST_Equals`, `ST_Disjoint`, `ST_Intersects`, `ST_Touches`,`ST_Crosses`, `ST_Within`, `ST_Contains`, and `ST_Overlaps` evaluate whether the corresponding spatial relationship holds between two input geometries, and return a boolean value. The function ST Distance returns a real number representing the minimum distance between the two geometries. Other functions return the geometries resulting from the application of geometric operations (`ST_Buffer` and `ST_ConvexHull`) (cf. Figure 5) or set-based operations (e.g. `ST_Intersection`,`ST_Difference`, `ST_Union`, `ST_SymDifference`) (cf. Figure 6) .

<img width="400" alt="Figure 5" src="https://github.com/user-attachments/assets/9282e9ba-020e-4863-9013-e3e50dc68552" />

<img width="400" alt="Figure 6" src="https://github.com/user-attachments/assets/3ea41c1f-7bee-4098-9e73-b66b5a24d647" />

An extensive presentation of all these geometry processing functions is available on [PostGIS website](https://postgis.net/docs/reference.html#Geometry_Processing).
The query in the following SQL example illustrates the use of such spatial functions. It searches for ships (name and unique identifier, i.e. the ship MMSI) that stopped within 500m of the oil rig "DRAUGEN". For each ship,the name of the oil rig and the time spent by the vessel close to Draugen is also shown.


> [!TIP]
The distance between ship positions and port locations is calculated using the PostGIS function `ST_dWithin`. The distance threshold (500m) can be visualised by creating a buffer around each location using the function `ST_Buffer`. 


```sql
SELECT mmsi, facname, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
SELECT facname, mmsi, min(datetime) as min_t , max(datetime) as max_t FROM context_data.oil_gas_infrastructure as q1
INNER JOIN ais_data.dynamic_ships as q2
ON (
    speed<2
    AND t>='2023-02-11 00:00:00'
    AND t<'2023-02-12 00:00:00'
    AND ST_dWithin(q1.geom_geo::geography,q2.geom::geography,500)
    )
WHERE facname = 'DRAUGEN'
GROUP BY facname, mmsi) as q3
LEFT JOIN ais_data.ships as q4 
ON (q3.mmsi=q4.sourcemmsi);
```

## Task 7!
- [ ] What vessel has been close to Draugen during 11. February? For how long was it within 500, and what type of ship is it?
- [ ] Visualize the vessels movement during 11. February.

### 5.1 Spatial indexes
Similar to classical SQL queries, spatial queries can be optimised using indexes
applied to spatial columns. PostGIS supports the GiST index, which indexes the
bounding boxes, or minimum rectangles, enclosing the spatial extent of the geometries in a geometric column. For instance, the bounding boxes of the geometries in Figure 7.a are depicted in Figure 7.b as gray, dotted rectangles, and highlighted by coloured rectangles in Figure 7.c. The example below shows how to create a GiST index on the geometry column `geom` of table `dynamic_ships`.

<img width="400"  alt="Figure 7" src="https://github.com/user-attachments/assets/510fa330-d313-49cf-be99-e5e53335ab07" />


```sql
CREATE INDEX idx_dynamic_ships_geom
ON ais_data.dynamic_ships
USING GiST (geom);
```

Bounding boxes allow for a compact, while simplified, representation of geometries, that can be used for efficiently comparing the geometries in spatial queries. When a SQL query refers to an indexed geometry, a spatial relationship is firstly evaluated using the spatial extent of the geometry (Figure 7.c). Afterwards, only for the subset of the potentially matching geometries, the exact spatial relationship is
processed and refined. In the example of Figure 7, a query on (a) searching for intersecting geometric objects would exclude the yellow circle, because its bounding box does not intersect with any other geometric object’s bounding box. The precise computation of the intersection is performed only between the blue pentagon and both the red line and green triangle (as they are the only boxes to overlap). With the index, the computation of the complex polygon intersection requires only two comparisons (first between the blue pentagon and the red line, then between the blue pentagon and the green triangle). Checking every geometric object with each other would have required 6 comparisons.

### 5.2 Create Data Analysis
In order to store the data analysis and the results of the data analysis queries that will be presented in the following sections, the creation of a new schema named `data_analysis` is required.



### 5.3 Detecting stops
The analysis of vessel movement begins with the identification of stops. A stop can be defined as a temporally ordered sequence of vessel positions with speed (i.e. speed over ground, SOG) equal to zero or below a very low threshold. The queries presented in the next examples create, for each vessel, the sequences of stops extracted from the history of the vessel’s positions. To build this sequence, first, an auxiliary table of successive position pairs, namely segments is created. For each ship, this table enables us to connect with a line segment every consecutive pair of AIS positions. The table is ordered according to the MMSI number and the position timestamp (ORDER BY mmsi, t), and the PostgreSQL function LEAD will be used to access the data in the next row of an ordered table.

From this table, for each vessel, stop events can be extracted and filtered according to the vessel speed that is associated to the preceding and the following positions of each segment. This table is also useful to detect transmissions gaps between vessel positions and GPS malfunctions
(e.g. detecting unfeasible speeds. A new index combining the vessels’ MMSI and the timestamp of the vessels’ positions is created to optimise the query. The SQL commands for creating the index and the table are given in the example below.

> [!WARNING]
Consider what vessels you want to detect stops for. Running the queries below on the complete dataset will be time consuming and mostly detect vessels already in port.


```sql
--create index on mmsi and time static data
CREATE INDEX idx_dynamic_ships_mmsi_t ON ais_data.dynamic_ships USING btree (mmsi,t);


--create segments table and populate from dynamic_ships
CREATE TABLE data_analysis.segments AS SELECT mmsi, -- ship identifier
t1,t2, -- starting and ending timestamps
speed1,speed2 , -- starting and ending speeds
p1,p2 , -- starting and ending points
st_makeline(p1,p2) as segment, -- line segment connecting points
st_distance(p1,p2) as distance, -- distance between points 
extract(epoch FROM (t2-t1)) as duration_s, -- timestamps in seconds 
  CASE WHEN extract(epoch FROM (t2-t1)) > 0
       THEN (st_distance(p1,p2)/extract(epoch FROM (t2-t1))) 
       ELSE NULL END as speed_m_s -- speed in m/s
FROM (
  SELECT mmsi, -- ship identifier
    LEAD(mmsi) OVER (ORDER BY mmsi,t ) as mmsi2 , -- next MMSI
    t as t1, -- starting time 
    LEAD(t) OVER (ORDER BY mmsi,t) as t2,--ending time
    speed as speed1 , -- initial speed
    LEAD(speed) OVER(ORDER BY mmsi,t) as speed2,--final speed
    geom as p1, -- initial point
    LEAD(geom) OVER (ORDER BY mmsi,t) as p2 -- final point
  FROM ais_data.dynamic_ships) as q1
WHERE mmsi=mmsi2; -- filter out different mmsi 

CREATE INDEX idx_segments_speed ON data_analysis.segments USING btree (speed1,speed2) ;
```

Once the table `segments` is created, stop events can be detected. Each stop starts immediately after a move, and ends as soon as the vessel starts moving again. Starting from the data in table segments, segments whose initial speed is above the speed threshold, and whose final speed is below the speed threshold, represent the beginning of stops (i.e. the vessel decreases its speed and goes steady). The end of a stop event is detected conversely.

The following example creates the auxiliary tables `stop_begin` and `stop_end`, which contain the potential starting and ending positions of vessel stops, selected as just described. In this example, a speed threshold of 0.1 knot is used. To optimise the future access to these tables, indexes are created.


```sql
--create stop_begin and stop_end tables
CREATE TABLE data_analysis.stop_begin AS -- first stop position
SELECT mmsi, t2 as t_begin -- stop starts at first steady position
FROM data_analysis.segments
WHERE speed1 >0.1 AND speed2 <=0.1; -- speed threshold is 0.1 kn

CREATE INDEX idx_stop_begin_mmsi_t ON data_analysis.stop_begin USING btree (mmsi,t_begin);

CREATE TABLE data_analysis.stop_end AS -- last stop position
SELECT mmsi, t1 as t_end -- stop ends at last steady position
FROM data_analysis.segments
WHERE speed1 <=0.1 AND speed2 >0.1; -- speed threshold is 0.1 kn
CREATE INDEX idx_stop_end_mmsi_t ON data_analysis.stop_end USING btree (mmsi,t_end);
```

Afterwards, the table stops is created by coupling, for each ship, `stop_begin` and `stop_end`, as illustrated in the following example (note that stops are ordered by time, that is, `ORDER BY t_end`).

```sql
CREATE TABLE data_analysis.stops AS SELECT mmsi, -- ship identifier
t_begin , -- start of the stop event
t_end , -- end of the stop event
extract(epoch FROM (t_end-t_begin)) as duration_s -- stop in seconds
FROM data_analysis.stop_begin INNER JOIN LATERAL ( -- keep only stops that have an end
SELECT t_end
FROM data_analysis.stop_end
WHERE stop_begin.mmsi=stop_end.mmsi AND
t_begin<=t_end -- stop follows the beginning
ORDER BY t_end LIMIT 1 -- select only the first stop end 
) AS q2 ON (true);

```

Congratulations you have come this far! Now it´s time for Iron Foxes!




[^1]: Laurent Etienne, Cyril Ray, Elena Camossi, Clément Iphar. Maritime Data Processing in Relational Databases. Guide to Maritime Informatics, Springer International Publishing, pp.73-118, 2021, 10.1007/978-3-030-61852-0_3. hal-03137050
