# Maritime data analysis with AIS: from raw data to situational awareness (hopefully)
 
All vessels above a certain size are required to carry an AIS transponder. Along the Norwegian coast there is therefore a constant stream of data on position, speed, course and identity transmitted via AIS (Automatic Identification System). [NAIS – BarentsWatch](https://nais.kystverket.no/) is a service that visualises all AIS data in Norwegian waters in near real time. My claim is that each message on its own is of little interest. Combined with contextual data such as pipelines, subsea cables, oil installations and military locations, however, the messages can reveal patterns, anomalies and activity of significance to the Norwegian Armed Forces and to society at large.
 
This week you will build a simple maritime information system, using PostgreSQL/PostGIS as the database and QGIS for visualisation. The dataset comes from Kystverket's historical AIS service. It covers October 2025, from Bodø and northwards, and contains several tens of millions of positions.
 
During the week you will:
 
* clean and import raw AIS data and contextual data into a geodatabase
* structure the data with schemas, tables, views and indexes so that queries run fast enough to be useful
* visualise vessel tracks in QGIS
* use spatial queries to find vessels near critical infrastructure, identify stops and map the "shadow fleet"
* assess the quality and limitations of the data
The assignment is based on the chapter [Maritime Data Processing in Relational Databases](https://hal.science/hal-03137050/file/Maritime_Informatics_2021.pdf) (Etienne et al., 2021), which is recommended as background reading.
 
## Before Tuesday: install the software
 
Download and install the following:
 
* **PostgreSQL** with the **PostGIS** extension ([postgresql.org/download](https://www.postgresql.org/download/)). On Windows, the installer ends by opening *Stack Builder*: choose *Spatial Extensions → PostGIS* there.
* **pgAdmin** ([pgadmin.org](https://www.pgadmin.org)). It is usually included in the PostgreSQL installer on Windows.
* **QGIS** ([qgis.org](https://www.qgis.org)). Choose the *Long Term Release*.
* **Python 3** ([python.org](https://www.python.org)). On Windows, tick *Add python.exe to PATH* during installation. Then run `pip install psycopg2-binary` in a terminal. Python is needed for the cleaning and import scripts.
* **The dataset:** [download the dataset here](LINK). Unpack it to a folder you can find again, with no spaces or special characters in the path.
> **Installation**
> Check that everything works: open pgAdmin and connect to your PostgreSQL server, open QGIS, and run `python -c "import psycopg2"` in a terminal without getting an error.
>
> **Submit in Canvas:** Screenshots showing that pgAdmin is connected to your server, that QGIS opens, and that the dataset is unpacked on your machine.
 
## Contents
 
* [Overview and schedule](#overview-and-schedule)
* [Inspect and clean the raw data](#inspect-and-clean-the-raw-data)
* [2.1–2.3 Creating the database and importing the data](#2123-creating-the-database-and-importing-the-data)
* [2.4–2.5 Geometry and indexes](#2425-geometry-and-indexes)
* [Checkpoint: Wednesday 10:00](#checkpoint-wednesday-1000)
* [3.1 Contextual data and the sanctions list](#31-contextual-data-and-the-sanctions-list)
* [3.2–3.4 Country codes, a view of the ships and relationships](#3234-country-codes-a-view-of-the-ships-and-relationships)
* [Part 4 – Visualising AIS tracks in QGIS](#part-4--visualising-ais-tracks-in-qgis)
* [5.1–5.4 Spatial queries and the shadow fleet](#5154-spatial-queries-and-the-shadow-fleet)
* [5.5 Who was close to Goliat?](#55-who-was-close-to-goliat)
* [5.6 Stops near critical infrastructure](#56-stops-near-critical-infrastructure)
* [5.7 Going dark (advanced)](#57-going-dark-advanced)
---
 
## Overview and schedule
 
This week you will build a maritime information system from scratch, fill it with real AIS data from Kystverket, and use it to analyse what vessels are doing along the coast of Northern Norway. The week ends with **Iron Foxes**, where you use your system to produce an intelligence report.
 
Some of the steps take from 20 minutes to several hours to run. The schedule below is built around this: start the slow jobs early, let the slowest ones run overnight from Tuesday to Wednesday, and use the waiting time on the next steps. If you fall behind, use the checkpoint on Wednesday to catch up.
 
| Day | Time | Content | Tasks |
|---|---|---|---|
| **Tuesday** | 12:00–13:00 | Introduction | |
| | 13:00–15:30 | **Part 2.1–2.3:** inspect and clean the data, create the database, import static data and position data. **Before you leave:** start the geometry steps in 2.4, and let them run overnight | Task 1, Task 2 |
| **Wednesday** | 08:00–10:00 | **Part 2.4–2.5:** finish the geometry and indexes. **While you wait:** Part 3.1, import the contextual data in QGIS | Task 3, Task 4 |
| | 10:00 | **Checkpoint.** Behind schedule? Restore the database backup | Checkpoint quiz |
| | Before lunch | **Part 3.2–3.3:** country codes and a view of the ships | Task 5 |
| | After lunch | **Part 4:** visualising AIS tracks in QGIS | Task 6 |
| **Thursday** | Before lunch | **Part 5.1–5.5:** spatial queries, Russian-flagged vessels, the shadow fleet, Goliat | Task 7, Task 8 |
| | After lunch | **Part 5.6–5.7:** stops near critical infrastructure, going dark | Task 9, Task 10 (advanced) |
| **Friday** | 08:00–15:30 | **Iron Foxes – INTREP 11** | |
 
> 🎯 **Where you should be:**
> * **Tuesday 15:30:** The import of the position data (Task 2) is finished, and the geometry steps in 2.4 are running. Keep the computer plugged in and awake overnight.
> * **Wednesday 10:00:** Geometry columns and indexes are in place, and the contextual data are imported.
> * **Wednesday 15:30:** You can show the track of a vessel on a map.
> * **Thursday 15:30:** You have found stops near critical infrastructure, and you are ready for Iron Foxes.
 
**Software:** PostgreSQL with PostGIS, pgAdmin, QGIS and Python (with the `psycopg2-binary` package) must be installed before Tuesday. See the introduction page for links and the dataset.
 
---
 
## Inspect and clean the raw data
 
The dataset comes directly from Kystverket's AIS service. Raw AIS data often contain errors, inconsistencies and missing values, caused by transmission problems, manual input by ship crews, or system limitations. Cleaning the data before importing it into the database matters for several reasons:
 
* **Accuracy:** invalid MMSI numbers, impossible positions or malformed timestamps lead to wrong analyses and misinterpretation of vessel behaviour.
* **Error prevention:** the database checks the data type of every column. A single badly formatted value can make the whole import fail.
* **Consistency:** standardised formats for timestamps, names and ship types make queries and joins reliable.
* **Performance:** duplicates and invalid rows slow down both the import and the queries afterwards.
### The cleaning script
 
Download the scripts from the [`scripts` folder on GitHub](https://github.com/KS-ingenior/oppgave_ais/tree/main/scripts) (`clean_ais.py` and `import_ais.py`), and save them in a folder on your machine. The cleaning script `clean_ais.py` goes through all the CSV files in a folder and:
 
* works out whether each file contains position data or static data, with or without a header row
* **removes the whole row** if an essential value is wrong: the wrong number of fields, a missing or invalid timestamp or MMSI, or an invalid position or one far outside the area
* **empties the value, but keeps the row,** if another value is outside the allowed range, for example a course of 400 or an IMO number written as `IMO9123456`. This way a valid position is not lost because of one bad value. The emptied values become `NULL` in the database.
* searches all the subfolders, so it handles the structure of the dataset, with one folder per day (`ais-data/position/date_utc=2025-10-01/...`)
* writes the rows that are kept to the folder `ais-data/cleaned`, with names such as `position_2025-10-01_CLEAN.csv`. The original files are not changed.
* prints how many rows were removed and how many values were emptied in each file, and why
On purpose, the script does **not** remove duplicate rows, and it keeps the special values that mean "not available" (course `360`, heading `511` and speed `102.3`). You will deal with these yourself later.
 
The script does not catch everything. That is why you will first look at the data yourself.
 
> **Task 1: What is a valid value?**
>
> 1. Open one CSV file from the position data, e.g. `ais-data/position/date_utc=2025-10-01/part-...csv`. Use a text editor (e.g. Notepad++ or VS Code) rather than Excel: Excel may silently reformat dates and numbers. The first line is the header, with the names of the columns.
> 2. For each of the columns in the table below, find out which values are **valid**. Use what you know (a latitude is an angle north or south of the equator) and search the web if you need to (e.g. "AIS true heading 511").
>
>    | Column | Unit or meaning | Valid values |
>    |---|---|---|
>    | `lat` | degrees north/south | ? |
>    | `lon` | degrees east/west | ? |
>    | `speed` | speed over ground, knots | ? |
>    | `course_over_ground` | direction of movement, degrees | ? |
>    | `true_heading` | the direction the bow points, degrees | ? |
>    | `mmsi` | identity of the AIS transmitter | ? |
>    | `status` | navigational status, a code | ? |
>
> 3. Some columns use a special value to say **"not available"**. Which values are these for `speed`, `course_over_ground` and `true_heading`? Use the search function in the editor (Ctrl+F or Cmd+F) to find at least one example of each in the file.
> 4. Can you find any **other** values in the file that look wrong or strange, e.g. empty fields, impossible values or odd text?
> 5. Run the cleaning script. Open a terminal in the folder where you saved the script, and give it the path to the `ais-data` folder, for example `python clean_ais.py "C:\path\to\ais-data"`. The script cleans both the position data and the static data, and puts the cleaned files in `ais-data/cleaned`. Look at the summary at the end: what were the most common reasons for removing rows or emptying values?
>
> **Submit in Canvas:** Copy the table into the text box and fill in the valid values. Then answer questions 3–5 briefly, with an example from the file for each answer (copy the line or the value).
 
---
 
## 2.1–2.3 Creating the database and importing the data
 
> 🎯 **Goal:** By **Tuesday 15:30** the position data should be imported (Task 2). By the **checkpoint on Wednesday at 10:00** all AIS data and contextual data should be imported, indexed and ready, so that the rest of the week can be spent on visualisation and analysis. Some steps take from 20 minutes to several hours to run. Start them early and use the waiting time on the next steps.
>
> **Strong recommendation:** Start the queries on the page **2.4–2.5 Geometry and indexes** before you leave on Tuesday, and let them run overnight. Keep the computer plugged in, with the lid open, and make sure it does not go to sleep. If it does, the query stops and has to be started again.
> * **Windows:** *Settings → System → Power & battery → Screen and sleep*: set sleep to *Never* when plugged in.
> * **Mac:** open a separate Terminal window and run `caffeinate -i`. Leave it open until the queries are done.
 
### 2.1 Create the database
 
Open pgAdmin and connect to your PostgreSQL server using the credentials you chose during installation. Open the Query Tool (*Tools → Query Tool*) and create a new, empty database:
 
```sql
CREATE DATABASE ingof3205;
```
 
> 🔍 **What the query does**
> * `CREATE DATABASE ingof3205` creates a new, empty database called `ingof3205`. The database is the top-level container: all tables, views and functions in this assignment will live inside it. You only run this once.
 
Select the new database in the browser panel on the left, open a new Query Tool **on that database**, and run:
 
```sql
-- Enable spatial data types and functions
CREATE EXTENSION postgis;
 
-- Create the schemas used in this assignment
CREATE SCHEMA ais_data;       -- AIS data (static and dynamic)
CREATE SCHEMA context_data;   -- pipelines, cables, installations, sanctions list, etc.
CREATE SCHEMA data_analysis;  -- the results of your analyses
 
-- Check that PostGIS works (should return a version number)
SELECT PostGIS_Version();
```
 
> 🔍 **What the query does**
> * Lines starting with `--` are comments. PostgreSQL ignores them; they are there to explain the code to you.
> * `CREATE EXTENSION postgis` installs PostGIS in this database: data types for geometries (points, lines, polygons) and several hundred spatial functions, all with names starting with `ST_`. Extensions are installed per database, which is why you must run this in `ingof3205` and not in the default database `postgres`.
> * `CREATE SCHEMA` creates a named workspace inside the database, a bit like a folder. From now on you refer to tables as `schema.table`, for example `ais_data.static_ships`.
> * `SELECT PostGIS_Version()` calls a function and shows the result. If PostGIS is installed correctly you get a version number; if not, you get an error.
 
> 💡 **Tip: Upper and lower case.** PostgreSQL converts all unquoted table and column names to lower case. If you want capital letters, you must put the name in double quotes (`"TableName"`), and then you must use the quotes every time you refer to it. Save yourself the trouble and use lower case names only. Note that double quotes are used for names, while single quotes (`'text'`) are used for string values.
 
**Why schemas?** A database can be organised into several schemas, each acting as a separate workspace. This makes it easier to:
 
* keep related tables, views and functions together in logical groups
* use the same table or function name in different schemas without conflicts
* give users and groups access only to the data they need
### 2.2 Static ship data
 
AIS transceivers on board vessels broadcast two kinds of messages: **dynamic** messages with position, speed and course, and **static** messages describing the vessel itself, such as name, callsign (the vessel's radio identifier), IMO number, ship type and dimensions. Each transceiver has its own Maritime Mobile Service Identity (MMSI), which is assigned by the flag state and identifies the source of every message.
 
In the static table, the MMSI column is called `sourcemmsi`, while in the position table it is called `mmsi`. The different names are deliberate: when you join the two tables, it is always clear which table a column comes from (`d.mmsi = s.sourcemmsi`), and you avoid ambiguous column names in the result.
 
The static files from Kystverket's historical AIS service look like this:
 
```text
mmsi,date_time_utc,msg_type,call_sign,ship_name,ship_type,to_bow,to_stern,to_port,to_starboard,length,breadth,ais_class,is_public,imo,draught,destination,dsrc
538007497,2025-10-01T01:20:00.000Z,5,"",PARTNERSHIP,0,0,0,0,0,0,0,A,true,9597848,0.00,"",S
```
 
The static messages go into the table `ais_data.static_ships`. As for the position data, the columns are in **the same order as in the file**, so the import can map them by position:
 
```sql
CREATE TABLE ais_data.static_ships (
  sourcemmsi    integer,           -- mmsi:          MMSI of the vessel's AIS transceiver
  timestamp_utc timestamptz,       -- date_time_utc: when the message was received (UTC)
  msg_type      integer,           -- msg_type:      AIS message type (5 = class A, 24 = class B)
  callsign      text,              -- call_sign:     radio callsign
  shipname      text,              -- ship_name:     vessel name as reported
  shiptype      integer,           -- ship_type:     ship type code (see 3.3)
  to_bow        integer,           -- distance from the AIS antenna to the bow (m)
  to_stern      integer,           -- ... to the stern (m)
  to_port       integer,           -- ... to the port side (m)
  to_starboard  integer,           -- ... to the starboard side (m)
  length        double precision,  -- length (m)
  breadth       double precision,  -- breadth (m)
  ais_class     text,              -- ais_class:     A or B
  is_public     boolean,           -- is_public:     false = not shown in Kystverket's open AIS services
  imo           integer,           -- imo:           IMO number, the vessel's international identification number
  draught       double precision,  -- draught:       current draught (m), entered by the crew
  destination   text,              -- destination:   destination as reported
  data_source   text,              -- dsrc:          how the message was received
  id            bigserial PRIMARY KEY  -- auto-generated row identifier, not in the file
);
```
 
> 🔍 **What the query does**
> * `CREATE TABLE ais_data.static_ships (...)` creates an empty table in the schema `ais_data`. Each line inside the parentheses defines one column: first the name, then the data type.
> * The data types decide what each column can hold: `integer` (whole numbers), `double precision` (decimal numbers), `text` (text of any length), `timestamptz` (date and time with time zone) and `boolean` (`true` or `false`).
> * `bigserial` is a whole number that PostgreSQL fills in automatically, 1, 2, 3 … for each new row. `PRIMARY KEY` means that the value must be unique and can never be empty, so that every row can be identified.
> * The data types also work as a check: if the file contains text in a column defined as `integer`, the import fails. This is why the files must be cleaned first (Task 1).
 
Column list to use with COPY or pgAdmin (everything except `id`):
 
```sql
(sourcemmsi, timestamp_utc, msg_type, callsign, shipname, shiptype, to_bow, to_stern,
 to_port, to_starboard, length, breadth, ais_class, is_public, imo, draught,
 destination, data_source)
```
 
> 🔎 **Zero often means "unknown".** In the static data, `0` is used for values the crew has not entered: ship type `0`, IMO `0`, draught `0.00` and dimensions `0`. A ship with length 0 is not a very small ship, it is a ship that has not reported its length. Keep this in mind before you calculate averages or filter on size. Missing text values also come in two forms: an empty field (`,,`) is imported as `NULL`, while an empty quoted field (`,"",`) is imported as an empty string `''`. Both mean the same thing, but `WHERE shipname IS NULL` only finds the first kind.
 
#### Loading the data
 
The static data are stored with one subfolder per day, each with a CSV file. Import the **cleaned** files in `ais-data/cleaned` that you created in Task 1, not the raw files.
 
**Recommended:** Use the import script `import_ais.py`, which you downloaded together with the cleaning script. Open a terminal in the folder where you saved it, and give it the path to the `cleaned` folder and the word `static`:
 
```bash
python import_ais.py "C:\path\to\ais-data\cleaned" static
```
 
The script asks for your PostgreSQL password, finds all the `_CLEAN.csv` files, and loads the files with static data into `ais_data.static_ships`. The word `static` at the end makes sure that only the static data are imported now; the position data come in Task 2. Each file is imported in its own transaction: if one file fails, nothing from that file is imported, and the script continues with the next one. If your database, user or port is not `ingof3205`, `postgres` and `5432`, change the settings at the top of the script.
 
**Alternative for single files:** In pgAdmin, right-click the table → *Import/Export Data…* → *Import*. Choose the file, set *Format* to `csv`, turn *Header* on, set *Delimiter* to `,`, and on the *Columns* tab remove the `id` column so that it is generated automatically.
 
> ⚠️ **Warning:** You may see examples using `COPY ... FROM '<path>'`. This command reads the file from the **database server's** file system, not your own user account, and often fails with "permission denied" on Windows. Use the script or the pgAdmin import instead.
 
#### First queries and your first index
 
When the import is done, check what you have:
 
```sql
-- Number of static messages
SELECT count(*) FROM ais_data.static_ships;
 
-- Number of different ship names
SELECT count(DISTINCT shipname) FROM ais_data.static_ships;
```
 
> 🔍 **What the query does**
> * `SELECT ... FROM ais_data.static_ships` reads from the table.
> * `count(*)` counts the rows: here, the number of static messages.
> * `count(DISTINCT shipname)` counts how many *different* values there are in the column `shipname`. A name that appears in 1000 rows is counted once. Empty values (`NULL`) are not counted.
 
Now let's see what an index does. First pick an MMSI that exists in the table:
 
```sql
SELECT sourcemmsi FROM ais_data.static_ships LIMIT 1;
```
 
> 🔍 **What the query does**
> * `SELECT sourcemmsi` returns only the column `sourcemmsi`.
> * `LIMIT 1` stops after the first row. Which row you get is not defined, but any MMSI will do here.
 
Insert that number in the query below, run it and note the *Execution Time* at the bottom of the output:
 
```sql
EXPLAIN ANALYZE
SELECT * FROM ais_data.static_ships WHERE sourcemmsi = <your MMSI>;
```
 
> 🔍 **What the query does**
> * `SELECT *` returns all columns.
> * `WHERE sourcemmsi = <your MMSI>` keeps only the rows where the condition is true. Replace `<your MMSI>` with the number, without the `< >`.
> * `EXPLAIN ANALYZE` in front of a query runs it, but instead of the result it shows the **query plan**: how PostgreSQL found the rows and how long each step took. Look at the type of scan (*Seq Scan* or *Index Scan*) and the *Execution Time* at the bottom.
 
The output shows a **Seq Scan**: PostgreSQL has to read every single row in the table to find the matching ones. Now create an index on the column and run the same query again:
 
```sql
CREATE INDEX idx_static_ships_mmsi ON ais_data.static_ships (sourcemmsi);
 
EXPLAIN ANALYZE
SELECT * FROM ais_data.static_ships WHERE sourcemmsi = <your MMSI>;
```
 
> 🔍 **What the query does**
> * `CREATE INDEX idx_static_ships_mmsi ON ais_data.static_ships (sourcemmsi)` builds an index on the column `sourcemmsi`. The name of the index is your own choice; a common convention is `idx_<table>_<column>`. If nothing else is specified, PostgreSQL makes a **B-tree** index, which keeps the values sorted.
> * The `EXPLAIN ANALYZE` query is the same as before, so that you can compare the plan and the time with and without the index.
 
The plan should now show an **Index Scan** or **Bitmap Index Scan**, and the execution time should be considerably lower. An index works like the index at the back of a book: instead of reading every page, you look up the term and go straight to the right page.
 
### 2.3 Movement data
 
The static information tells us *who* the vessels are. To analyse *where* they go, we need their positions, which are stored in the folder `ais-data/position`.
 
The position files come from Kystverket's historical AIS service and look like this:
 
```text
date_time_utc,mmsi,dsrc,lon,lat,status,rate_of_turn,speed,course_over_ground,true_heading,ais_class
2025-10-01T15:45:16.000Z,257456220,G,19.494259,70.24205,0,0,0.10,360.00,511,B
```
 
```sql
CREATE TABLE ais_data.dynamic_ships (
  timestamp_utc timestamptz,       -- date_time_utc:      when the position was received (UTC)
  mmsi          integer,           -- mmsi:               MMSI of the transmitting vessel
  data_source   text,              -- dsrc:               how the message was received
  lon           double precision,  -- lon:                longitude
  lat           double precision,  -- lat:                latitude
  status        integer,           -- status:             navigational status code (see below)
  rate_of_turn  double precision,  -- rate_of_turn:       rate of turn
  speed         double precision,  -- speed:              speed over ground (knots)
  course        double precision,  -- course_over_ground: course over ground (degrees)
  heading       integer,           -- true_heading:       true heading (degrees)
  ais_class     text,              -- ais_class:          A (larger, mandatory) or B (smaller vessels)
  id            bigserial PRIMARY KEY
);
```
 
> 🔍 **What the query does**
> * The table is built in the same way as `static_ships`: one line per column, with name and data type, in the same order as the columns in the file.
> * Some columns get shorter or clearer names than in the file: `data_source` instead of `dsrc`, `course` instead of `course_over_ground` and `heading` instead of `true_heading`. The comment at the end of each line shows the name in the file.
> * The file has no geometry: the position is only given as two numbers, `lon` and `lat`. You will turn them into a geometry in 2.4.
 
The import script translates the column names in the file to the names in the table. The `id` column is not in the file, and is generated automatically. If you import with COPY or pgAdmin instead of the script, list the columns explicitly, in the same order as in the file:
 
```sql
-- column list to use with COPY or pgAdmin (everything except id)
(timestamp_utc, mmsi, data_source, lon, lat, status, rate_of_turn,
 speed, course, heading, ais_class)
```
 
```sql
SELECT count(*) FROM ais_data.dynamic_ships;
```
 
> 🔍 **What the query does**
> * `count(*)` counts the rows in the table. On a table with tens of millions of rows this takes a while, because PostgreSQL has to go through the whole table to count them.
 
> 🔎 **Codes and "not available" values.** Several AIS fields use codes rather than plain values. The navigational status is a number: `0` under way using engine, `1` at anchor, `2` not under command, `3` restricted manoeuvrability, `5` moored, `6` aground, `7` engaged in fishing, `8` under way sailing, `15` not defined. Some fields also use special values that mean "not available": heading `511`, course `360` and speed `102.3`. These are not real measurements, and must be left out (or set to `NULL`) before you calculate averages or look for high speeds. The column `data_source` (`dsrc` in the file) shows how the message was received, probably `G` for a ground station and `S` for satellite. Look up the codes in Kystverket's documentation for the historical AIS data.
 
> **Task 2: Load the position data**
> Create the table `ais_data.dynamic_ships` using the SQL above, and import all the **cleaned** position files with `import_ais.py`, in the same way as the static data, but with the word `position` at the end:
>    `python import_ais.py "C:\path\to\ais-data\cleaned" position`
>
> This is the largest import of the day (several tens of millions of rows). Start it as early as you can. When it is done, run the count query above and note the number. You will need it at the checkpoint.
>
> **Submit in Canvas:** The number of rows in `ais_data.dynamic_ships`.
 
---
 
## 2.4–2.5 Geometry and indexes
 
### 2.4 Make it geographic
 
Ships move in a spatial context of coastlines, straits, ports, anchorages, restricted areas and seabed infrastructure. To relate vessel positions to that context, the positions must be stored as geometries rather than as two separate number columns.
 
PostGIS represents spatial objects as simple geometric features (vector data), each with a coordinate reference system (CRS):
 
* `POINT` – a single position
* `LINESTRING` – an ordered sequence of points (e.g. a pipeline or a vessel track)
* `POLYGON` – an area bounded by one outer ring and possibly inner rings (holes)
* `MULTIPOINT`, `MULTILINESTRING`, `MULTIPOLYGON` – sets of objects of the same type
* `GEOMETRYCOLLECTION` – a set of objects of different types
AIS positions are given in **WGS84**, the coordinate system used by GPS, which PostGIS identifies as **EPSG:4326**. All coordinate systems PostGIS knows about are listed in the table `public.spatial_ref_sys`.
 
The positions are stored as two separate number columns, `lon` and `lat`. In the first step below, you combine them into a point geometry in a new column, `geom`. In the second, you make a copy of the points in a coordinate system that uses metres.
 
With the full dataset, steps 1 and 2 can take several hours each, so start them **before you leave on Tuesday**. Paste all four steps into the Query Tool and run them together: pgAdmin runs them one after the other, and the last one may still be running when you come back on Wednesday morning.
 
```sql
-- 1. Geographic coordinates (WGS84) – used for display in QGIS
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom geometry(Point, 4326);
 
UPDATE ais_data.dynamic_ships
SET geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);
 
-- 2. Projected coordinates (metres) – used for distances and speeds
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom3035 geometry(Point, 3035);
 
UPDATE ais_data.dynamic_ships
SET geom3035 = ST_Transform(geom, 3035);
 
-- 3. Indexes (always create indexes AFTER bulk loading – it is much faster)
CREATE INDEX idx_dynamic_ships_geom     ON ais_data.dynamic_ships USING GiST (geom);
CREATE INDEX idx_dynamic_ships_geom3035 ON ais_data.dynamic_ships USING GiST (geom3035);
CREATE INDEX idx_dynamic_ships_mmsi_t   ON ais_data.dynamic_ships (mmsi, timestamp_utc);
 
-- 4. Clean up and update statistics
VACUUM ANALYZE ais_data.dynamic_ships;
```
 
> 🔍 **What the query does**
> * **Step 1:** `ADD COLUMN geom geometry(Point, 4326)` adds a new, empty column that may only hold points in the coordinate system 4326. `UPDATE ... SET geom = ...` fills it in for every row: `ST_MakePoint(lon, lat)` makes a point from the two numbers (note the order: longitude first, since it is the x coordinate), and `ST_SetSRID(..., 4326)` labels the point with SRID 4326 **without changing the coordinates**.
> * **Step 2:** `ADD COLUMN geom3035 geometry(Point, 3035)` adds a new, empty column. `UPDATE ... SET geom3035 = ST_Transform(geom, 3035)` fills it in for every row: `ST_Transform` **recalculates the coordinates** from degrees (4326) to metres (3035). Note the difference: `ST_SetSRID` only puts a label on the coordinates, while `ST_Transform` converts them.
> * **Step 3:** `USING GiST` makes a spatial index on the geometry columns (you will learn how it works in 5.2). `(mmsi, timestamp_utc)` is a **composite index**: sorted by MMSI, and by time within each MMSI. This is exactly what is needed to fetch the positions of one vessel in time order.
> * **Step 4:** `VACUUM ANALYZE` cleans up after the update and updates the statistics (see the box below).
 
> ⏳ **While you wait:** Don't sit and watch pgAdmin. Open the page **3.1 Contextual data and the sanctions list** and start importing the contextual data in QGIS.
 
> 🧭 **Why two geometry columns?** In EPSG:4326 the coordinates are in degrees. One degree of longitude is about 111 km at the equator, but only about 38 km at 70°N. Distances calculated in 4326 are therefore meaningless as metres. EPSG:3035 (ETRS89 / LAEA Europe) is a projected system with metres as its unit, which is what we need when calculating distances and speeds later.
 
> 🧹 **Why VACUUM?** An `UPDATE` in PostgreSQL does not overwrite rows. It writes a new version of each row and marks the old one as dead. After updating every row twice, in steps 1 and 2, the table contains twice as many dead rows as live ones. `VACUUM` frees that space, and `ANALYZE` updates the statistics the query planner uses to choose between a sequential scan and an index.
 
### 2.5 Make it faster
 
On a table with tens of millions of rows, a query without a suitable index can take minutes. The command `EXPLAIN ANALYZE` shows how PostgreSQL executes a query and how long each step takes.
 
Find the first and last timestamp in the dataset:
 
```sql
EXPLAIN ANALYZE
SELECT min(timestamp_utc), max(timestamp_utc) FROM ais_data.dynamic_ships;
```
 
> 🔍 **What the query does**
> * `min()` and `max()` are **aggregate functions**: they take the values from many rows and return one value. Here they return the earliest and the latest timestamp in the table.
> * `EXPLAIN ANALYZE` shows the plan and the time, as in 2.2.
 
The plan shows a sequential scan: every row is read to find the smallest and largest value. A **B-tree index** keeps the values sorted, which is efficient for anything with a natural order such as times, numbers and text. Create one and run the query again:
 
```sql
CREATE INDEX idx_dynamic_ships_time ON ais_data.dynamic_ships (timestamp_utc);
 
EXPLAIN ANALYZE
SELECT min(timestamp_utc), max(timestamp_utc) FROM ais_data.dynamic_ships;
```
 
> 🔍 **What the query does**
> * `CREATE INDEX ... (timestamp_utc)` builds a B-tree index on the time column. On this table it takes a few minutes.
> * The `EXPLAIN ANALYZE` query is the same as before, so that you can compare.
 
With the index, PostgreSQL only needs to look at the first and last entry. Indexes take time to build and use disk space, so create them on the columns you actually query often.
 
> **Task 3: Who was out on 22 October?**
> Find how many different ships broadcast their position on 22 October 2025, and list their names.
>
> 1. Which tables do you need? (Hint: the positions are in one table, the names in another.)
> 2. Write the query and run it with `EXPLAIN ANALYZE`. Is an index used?
> 3. Compare these two `WHERE` clauses. Which one can use the index on `timestamp_utc`, and why?
>    * `WHERE timestamp_utc::date = '2025-10-22'`
>    * `WHERE timestamp_utc >= '2025-10-22' AND timestamp_utc < '2025-10-23'`
>
> **Submit in Canvas:** Answer the quiz for Task 3.
 
---
 
## Checkpoint: Wednesday 10:00
 
Run these queries and note the results:
 
```sql
SELECT count(*) FROM ais_data.static_ships;
SELECT count(*) FROM ais_data.dynamic_ships;
SELECT count(*) FROM ais_data.dynamic_ships WHERE geom IS NULL;  -- should be 0
SELECT indexname FROM pg_indexes WHERE schemaname = 'ais_data';
```
 
> 🔍 **What the query does**
> * The first two queries count the rows in each table.
> * The third counts the positions that have no geometry. `IS NULL` is used because an empty value cannot be tested with `=`: `geom = NULL` is never true.
> * `pg_indexes` is a **system view**: a view that PostgreSQL maintains itself, listing all indexes in the database. `WHERE schemaname = 'ais_data'` limits the list to our AIS tables.
 
> 🛟 **Behind schedule?** Download the database backup and restore it in pgAdmin: right-click *Databases → Create → Database…* and name it `ingof3205`, then right-click the new database → *Restore…* and choose the backup file. This takes about 15 minutes, after which you are at the same point as everyone else.
 
> **Checkpoint**
> Enter the numbers in the checkpoint quiz, and tick off the indexes you have created.
>
> **Submit in Canvas:** The checkpoint quiz.
 
---
 
## 3.1 Contextual data and the sanctions list
 
AIS data on its own tells us where vessels are. To understand what they are *doing*, we need to know what is around them. The dataset includes contextual data such as Norwegian Armed Forces locations, oil and gas installations, pipelines and subsea cables. Unlike AIS, these data do not change from minute to minute, and they go in the schema `context_data`.
 
**How to import with QGIS:**
 
1. Add the file to QGIS as a layer (drag and drop works for most formats).
2. Open *Database → DB Manager*, expand *PostGIS*, connect to `ingof3205` and select the schema `context_data`.
3. Click *Import Layer/File*, choose the layer, and set:
   * **Table:** the table name from the table in Task 4 at the end of this page
   * **Target SRID:** `4326` (tick the box) – this reprojects the data to WGS84 during import
   * **Create spatial index:** ticked
   * **Convert field names to lowercase:** ticked
4. Click *OK*.
**Check the data types.** QGIS often imports numbers as text (`varchar`). Look through the columns of each table. If a column only contains numbers but is stored as text, change the type:
 
```sql
ALTER TABLE context_data.<table>
ALTER COLUMN <column> TYPE integer USING <column>::integer;
```
 
> 🔍 **What the query does**
> * `ALTER TABLE ... ALTER COLUMN ... TYPE integer` changes the data type of an existing column. Replace `<table>` and `<column>` with the actual names, without the `< >`.
> * `USING <column>::integer` says how each value is converted. `::` is PostgreSQL's **cast operator**: `'42'::integer` turns the text `'42'` into the number 42.
> * If a single value cannot be converted (e.g. `'n/a'`), the whole command fails and nothing is changed. Find the culprits with `SELECT <column> FROM context_data.<table> WHERE <column> !~ '^[0-9]+$';` (`!~` means "does not match the pattern", and the pattern means "only digits").
 
#### More contextual data from GT
 
The dataset only contains a few contextual layers. Many more geographic datasets are available in **GT**: [https://geotjenester/gt-client/home](https://geotjenester/gt-client/home). The link is not a public internet address, so it only works from the network you use in class.
 
Your job is to find data that can help you **explain or reveal** what vessels are doing. Think about what you will need in the analyses later in the week and in Iron Foxes, for example:
 
* ports, quays and anchorages
* fairways and traffic separation schemes
* restricted, firing and exercise areas
* territorial waters, baselines and fishing zones
* military installations and other critical infrastructure along the coast
When you download:
 
* Choose a format QGIS can read, preferably **GeoPackage** (`.gpkg`) or shapefile.
* Note which **coordinate system** the data are in. Norwegian data are often in EPSG:25833 (UTM zone 33). This is not a problem, since *Target SRID 4326* in DB Manager reprojects the data during the import.
* Note the **source and date** of each dataset. You will need it when you assess how reliable your results are, and when you write your report in Iron Foxes.
Import the data with the same steps as above, into the schema `context_data`. Choose table names in lower case, without spaces or special characters (e.g. `firing_areas`, `anchorages`).
 
#### The EU sanctions list
 
The sanctions list is **not** part of the dataset. The EU adds new vessels regularly, so you must download the latest version yourself from the Danish Maritime Authority: [EU sanction designated vessels | dma.dk](https://www.dma.dk/growth-and-framework-conditions/maritime-sanctions/general-information/eu-vessel-designations).
 
The list is published as a table on the web page, not as a file, so it takes a few steps to get it into the database:
 
1. Open the page and find the table of vessels designated under the **Russia/Belarus** sanctions. (The page also has a separate table for North Korea, with different columns. Leave that one out.)
2. Select the whole table, copy it, and paste it into Excel or LibreOffice Calc.
3. Check the result: one row per vessel, and the columns *vessel name*, *IMO number* and *date of application*. Remove any empty rows or repeated header rows.
4. Save the sheet as **CSV (UTF-8)**, for example `eu_designated_vessels.csv`.
5. Create the table and import the file with pgAdmin (*right-click the table → Import/Export Data… → Import*, *Header* on, and the delimiter your spreadsheet used when saving: `,` or `;`):
```sql
CREATE TABLE context_data.eudesignated (
  vessel_name         text,   -- may include former names, e.g. "Kavya (formerly Hana)"
  imo                 text,   -- converted to integer below
  date_of_application text    -- the date the sanctions apply from
);
```
 
> 🔍 **What the query does**
> * All columns are created as `text`, including the IMO number. A copied web table can contain spaces or other characters, which would make the import fail if the column were `integer`. The IMO number is converted to a number in the next step, after the import.
 
The IMO number must be an integer to be compared with the AIS data. Spreadsheets sometimes add spaces or other characters, so convert it like this:
 
```sql
ALTER TABLE context_data.eudesignated
ALTER COLUMN imo TYPE integer
USING NULLIF(regexp_replace(imo, '\D', '', 'g'), '')::integer;  -- keeps only the digits
 
-- Check: how many vessels, and how many without a valid IMO number?
SELECT count(*), count(*) FILTER (WHERE imo IS NULL) AS missing_imo
FROM context_data.eudesignated;
```
 
> 🔍 **What the query does**
> * `regexp_replace(imo, '\D', '', 'g')` replaces every character that is **not** a digit (`\D`) with nothing. `'g'` (global) means all occurrences, not just the first.
> * `NULLIF(..., '')` returns `NULL` if nothing is left (no digits at all). An empty text cannot be converted to a number, but `NULL` can.
> * `::integer` converts the remaining digits to a number.
> * In the check, `count(*)` counts all rows, while `count(*) FILTER (WHERE imo IS NULL)` counts only the rows that match the condition. One query thus gives both the total and the number without a valid IMO.
 
> 🧭 **Note the dates.** The sanctions list is from today, but the AIS data are from October 2025. Some of the vessels on the list were designated after the data were recorded. Use the column `date_of_application` when you interpret your results in Task 7: was the vessel already sanctioned when it was sailing along the Norwegian coast?
 
**Check the coordinate systems.** Spatial queries only work between geometries in the same CRS. This query lists all geometry columns in `context_data` with their CRS (`srid`) and type:
 
```sql
SELECT f_table_name, f_geometry_column, srid, type
FROM geometry_columns
WHERE f_table_schema = 'context_data';
```
 
> 🔍 **What the query does**
> * `geometry_columns` is a view that PostGIS maintains automatically. It lists every geometry column in the database, with the table name (`f_table_name`), column name (`f_geometry_column`), coordinate system (`srid`) and geometry type (`type`).
> * `WHERE f_table_schema = 'context_data'` limits the list to the contextual data.
 
All tables should have `srid` 4326. If a table was imported without reprojection, fix it like this:
 
```sql
ALTER TABLE context_data.<table>
ALTER COLUMN geom TYPE geometry(Geometry, 4326)
USING ST_Transform(geom, 4326);
```
 
> 🔍 **What the query does**
> * `ALTER COLUMN geom TYPE geometry(Geometry, 4326)` changes the column to the coordinate system 4326. `Geometry` (rather than `Point`) means that any geometry type is allowed, since the contextual tables contain points, lines and polygons.
> * `USING ST_Transform(geom, 4326)` recalculates every geometry from its current coordinate system to 4326.
> * This only works if the current SRID is correct. If `geometry_columns` shows `srid` 0, PostGIS does not know which system to convert from. Then you must first label the data with the correct original system using `ST_SetSRID`.
 
> **Task 4: Import the contextual data**
> Import the files below into the schema `context_data`, **using exactly the table names given**. The queries later in the assignment depend on these names.
>
> | File in the dataset | Table name in the database |
> |---|---|
> | Forsvarets_lokasjoner | `forsvarets_lokasjoner` |
> | cabel_geo | `cables` |
> | [oil and gas installations file] | `oil_gas_infrastructure` |
> | Oil pipeline | `oil_pipelines` |
> | Oil Refineries | `oil_refineries` |
> | EU sanctions list (download the **updated** list, see above) | `eudesignated` |
>
> Then find **at least two** more datasets in GT that you think are relevant for analysing vessel activity along the coast of Northern Norway. Download them and import them into `context_data`, with table names of your own choice.
>
> **Submit in Canvas:** A screenshot of DB Manager showing the tables in `context_data`, and the output of the CRS check query above. For each GT dataset, also give the table name, what the data show, where and when they were downloaded, and why they are relevant (1–2 sentences each).
 
---
 
## 3.2–3.4 Country codes, a view of the ships and relationships
 
### 3.2 Country codes from the MMSI
 
The first three digits of a ship's MMSI are the **Maritime Identification Digits (MID)**, which identify the flag state. MIDs are assigned to countries by the International Telecommunication Union (ITU), and the first digit shows the region: 2 is Europe, 3 North America and the Caribbean, 4 Asia (except the southeast), 5 the Pacific, Eastern Indian Ocean and Southeast Asia, 6 Africa, the Atlantic and Western Indian Ocean, and 7 South America. Norway has the MIDs 257, 258 and 259.
 
Create a lookup table that maps MID to country:
 
```sql
CREATE TABLE context_data.cnty_codes (
  digit   integer PRIMARY KEY,  -- 3-digit MID, e.g. 257
  country varchar(255)          -- country name
);
```
 
> 🔍 **What the query does**
> * `digit integer PRIMARY KEY` makes the MID the primary key: each MID can appear only once. If the file contains the same MID twice, the import fails. The key thus works as a built-in check of the data.
> * `varchar(255)` is text of at most 255 characters.
 
Import the file `AIS-country-codes.csv` with pgAdmin: right-click the table → *Import/Export Data…* → *Import*, *Format* `csv`, *Header* on, and **Delimiter `;`** (note: semicolon, not comma).
 
> 🔎 **Not all MMSI numbers belong to ships.** The MID only identifies a flag state for ship stations. MMSI numbers starting with `00` are coast stations, `111` are search and rescue aircraft, `970`–`979` are emergency devices (AIS-SART, MOB, EPIRB), and `99` are aids to navigation such as buoys. Also note that converting an MMSI to `integer` removes leading zeros. What does this mean for the country lookup in the view below?
 
### 3.3 A view of the ships
 
The table `static_ships` contains the same vessel many times, because static messages are automatically repeated at regular intervals. A **view** can collapse these repetitions into one row per vessel, translate the ship type code into text and add the country at the same time:
 
```sql
CREATE VIEW ais_data.ships AS
SELECT DISTINCT ON (s.sourcemmsi, s.imo, s.shiptype)
  s.sourcemmsi,
  NULLIF(s.imo, 0) AS imo,          -- 0 means "no IMO number"
  s.shiptype,
  CASE
    WHEN s.shiptype = 0               THEN 'Not available'
    WHEN s.shiptype BETWEEN 20 AND 29 THEN 'Wing in ground'
    WHEN s.shiptype = 30              THEN 'Fishing'
    WHEN s.shiptype IN (31, 32)       THEN 'Towing'
    WHEN s.shiptype = 33              THEN 'Dredging or underwater operations'
    WHEN s.shiptype = 34              THEN 'Diving operations'
    WHEN s.shiptype = 35              THEN 'Military operations'
    WHEN s.shiptype = 36              THEN 'Sailing'
    WHEN s.shiptype = 37              THEN 'Pleasure craft'
    WHEN s.shiptype BETWEEN 40 AND 49 THEN 'High speed craft'
    WHEN s.shiptype = 50              THEN 'Pilot vessel'
    WHEN s.shiptype = 51              THEN 'Search and rescue'
    WHEN s.shiptype = 52              THEN 'Tug'
    WHEN s.shiptype = 53              THEN 'Port tender'
    WHEN s.shiptype = 54              THEN 'Anti-pollution'
    WHEN s.shiptype = 55              THEN 'Law enforcement'
    WHEN s.shiptype = 58              THEN 'Medical transport'
    WHEN s.shiptype BETWEEN 60 AND 69 THEN 'Passenger'
    WHEN s.shiptype BETWEEN 70 AND 79 THEN 'Cargo'
    WHEN s.shiptype BETWEEN 80 AND 89 THEN 'Tanker'
    ELSE 'Other'
  END AS shiptype_text,
  s.callsign,
  s.shipname,
  NULLIF(s.length, 0)  AS length,   -- 0 means "not reported"
  NULLIF(s.breadth, 0) AS breadth,
  s.ais_class,
  c.country            AS cnty,
  c.digit              AS cnty_code,
  s.timestamp_utc      AS last_seen
FROM ais_data.static_ships s
LEFT JOIN context_data.cnty_codes c
  ON left(s.sourcemmsi::text, 3)::integer = c.digit
ORDER BY s.sourcemmsi, s.imo, s.shiptype, s.timestamp_utc DESC;
```
 
> 🔍 **What the query does**
> * `CREATE VIEW ais_data.ships AS` stores the query below under the name `ais_data.ships`. You can then use `ais_data.ships` as if it were a table, but the query is run again every time you use it.
> * `FROM ais_data.static_ships s` and `context_data.cnty_codes c`: `s` and `c` are **aliases**, short names for the tables. `s.shipname` means "the column `shipname` in the table `s`".
> * `DISTINCT ON (s.sourcemmsi, s.imo, s.shiptype)` keeps **one** row for each unique combination of the columns in the parentheses. Which row is kept is decided by `ORDER BY`: the rows are sorted by the same columns and then by time, newest first (`DESC`), so each vessel gets its most recently reported name and callsign. Without `ORDER BY`, PostgreSQL would pick an arbitrary row.
> * `CASE WHEN ... THEN ... ELSE ... END` works like *if – else if – else*: the conditions are tested from the top, and the first one that is true decides the value. Here it translates the ship type code into text. The codes are defined in the AIS standard (ITU-R M.1371): the first digit gives the main category (3 = special vessels, 6 = passenger, 7 = cargo, 8 = tanker), and for some categories the second digit gives more detail.
> * `NULLIF(x, 0)` returns `NULL` when x is 0, so that "unknown" is stored as unknown rather than as a number.
> * `AS` gives a column a new name in the result, e.g. `c.country AS cnty`.
> * `LEFT JOIN ... ON ...` adds the country from `cnty_codes`. *LEFT* means that all ships are kept, even those whose MID is not in the country table; they simply get `NULL` as country. A plain `JOIN` would drop them.
> * `left(s.sourcemmsi::text, 3)::integer` converts the MMSI to text, takes the first three characters, and converts them back to a number. The result is the MID, which is compared with `c.digit`.
 
> 🔎 **Some class B vessels appear twice.** Class A vessels send all their static information in one message (type 5). Smaller vessels with class B transceivers split it into two messages: type 24 **part A** with the name, and type 24 **part B** with the ship type, callsign and dimensions. In Kystverket's data the two parts are sometimes combined into one complete row (e.g. the fishing vessel TUNFISK, MMSI 257456220, with name, callsign, ship type and dimensions in the same row), and sometimes kept as separate rows. In the second case the vessel gets two rows in the view: one with a name but ship type *Not available*, and one with a ship type and dimensions but no name. Some vessels only ever appear with part B rows, and therefore never get a name at all in the database. For example, the Russian-flagged MMSI 273333850 has a part B row with ship type 52 (tug) and length 29 m, but no name. Use the callsign to identify these vessels. Keep this in mind in Task 5, and when you look up the name and type of a vessel later in the assignment.
 
> 💡 **Tip: Table, view or materialized view?**
> A **table** stores data physically on disk.
> A **view** is a stored query. It holds no data, and the query runs every time you use the view, so the result is always up to date, but it can be slow.
> A **materialized view** stores the result of the query on disk. It is fast to read, but it does not update automatically: you must run `REFRESH MATERIALIZED VIEW` when the underlying data changes. It is useful when a query is expensive and the data rarely changes.
 
### 3.4 How the tables relate to each other
 
Before you start combining tables, you need to know **how the rows in one table relate to the rows in another**. There are three kinds of relationships:
 
| Relationship | Meaning | Example in this database |
|---|---|---|
| **One-to-one (1:1)** | Each row in A matches at most one row in B, and the other way round | An IMO number and its entry in the sanctions list (`eudesignated`): each vessel should be listed only once |
| **One-to-many (1:N)** | One row in A matches many rows in B, but each row in B matches only one row in A | One MID in `cnty_codes` matches many vessels. One vessel (MMSI) has many positions in `dynamic_ships` |
| **Many-to-many (N:M)** | Rows in A can match many rows in B, and rows in B can match many rows in A | MMSI and IMO: a vessel (IMO) gets a new MMSI when it changes flag, and one MMSI can be used by several vessels (Task 5) |
 
In a well-designed database, relationships are enforced with keys. A **primary key** identifies each row uniquely (like `id` in our tables), and a **foreign key** points to the primary key of another table. A many-to-many relationship cannot be stored directly between two tables. It needs a third table in between, a **junction table**, with one row for each combination. In our database, `static_ships` works as such a table: each row links one MMSI to one IMO at a given time.
 
Our AIS data come from the real world, not from a designed system, so none of these relationships are enforced. **You have to find out for yourself what the relationship actually is**, and not assume it. Check how many IMO numbers each MMSI has, and how many MMSI numbers each IMO has:
 
```sql
-- MMSI numbers that have reported more than one IMO number
SELECT sourcemmsi, count(DISTINCT imo) AS n_imo
FROM ais_data.static_ships
WHERE imo <> 0
GROUP BY sourcemmsi
HAVING count(DISTINCT imo) > 1;
 
-- IMO numbers that have been reported by more than one MMSI
SELECT imo, count(DISTINCT sourcemmsi) AS n_mmsi
FROM ais_data.static_ships
WHERE imo <> 0
GROUP BY imo
HAVING count(DISTINCT sourcemmsi) > 1;
```
 
> 🔍 **What the query does**
> * `WHERE imo <> 0` leaves out rows without an IMO number (`<>` means "not equal to").
> * `GROUP BY sourcemmsi` collects all rows with the same MMSI into one group. Aggregate functions such as `count()` are then calculated per group, and the result has one row per MMSI.
> * `count(DISTINCT imo)` counts the number of *different* IMO numbers in each group.
> * `HAVING count(DISTINCT imo) > 1` keeps only the groups with more than one IMO number. `HAVING` is a filter that is applied **after** grouping. `WHERE` is applied before grouping, and cannot be used with aggregate functions.
> * The second query is the same, but the other way round: grouped by IMO, counting different MMSI numbers.
 
**Why this matters: joins multiply rows.** When you join a table to a table on the "many" side, each row is repeated once for every match. If you believe the relationship is one-to-many, but it is in fact many-to-many, the result silently gets more rows than it should. Compare these two ways of counting the positions of Russian-flagged vessels on 22 October:
 
```sql
-- A: IN only asks whether the MMSI is in the list
SELECT count(*)
FROM ais_data.dynamic_ships d
WHERE d.timestamp_utc >= '2025-10-22' AND d.timestamp_utc < '2025-10-23'
  AND d.mmsi IN (SELECT sourcemmsi FROM ais_data.ships WHERE cnty_code = 273);
 
-- B: JOIN repeats each position once for every matching row in the view
SELECT count(*)
FROM ais_data.dynamic_ships d
JOIN ais_data.ships s ON d.mmsi = s.sourcemmsi
WHERE d.timestamp_utc >= '2025-10-22' AND d.timestamp_utc < '2025-10-23'
  AND s.cnty_code = 273;
```
 
> 🔍 **What the query does**
> * Both queries limit the positions to one day with a time range, so that they run fast on the index.
> * **A:** The query in parentheses (a **subquery**) produces a list of all Russian MMSI numbers (MID 273). `d.mmsi IN (...)` keeps the positions whose MMSI is in the list. Each position is counted at most once, however many times the MMSI appears in the list.
> * **B:** `JOIN ais_data.ships s ON d.mmsi = s.sourcemmsi` combines each position with **every** row in the view that has the same MMSI. If an MMSI has two rows in the view, each position of that vessel appears twice in the result.
 
If B gives a higher number than A, some of the Russian MMSI numbers have more than one row in the view, and the join has counted their positions several times. No error message warns you about this: the query runs fine, and the numbers are simply wrong.
 
> 💡 **Tip: Check the row count before and after a join.** If the number of rows grows when you join, ask yourself whether it should. `IN (...)`, `EXISTS (...)` or a `LATERAL` subquery with `LIMIT 1` are ways of looking something up without multiplying rows.
 
The static information is entered manually by the crew and can be changed at any time. Names are missing, MMSI numbers are shared or reused, and IMO numbers are sometimes wrong. Keep this in mind for the rest of the assignment: the data can be wrong, and sometimes deliberately so.
 
> **Task 5: How reliable is the static data?**
> Using the view `ais_data.ships`, answer the following:
>
> 1. How many ships have a ship name that is null, empty or only spaces?
> 2. How many MMSI numbers appear more than once?
> 3. How many ships have the ship type *Not available*, and how many have no IMO number?
> 4. Based on your answers: can `sourcemmsi` or `shipname` be used as a primary key? Why or why not?
>
> Then look at the table `static_ships` itself (not the view):
>
> 5. How many class B vessels (`ais_class = 'B'`) have more than one row in the view? Look at a few of them: how do the rows differ, and what does this mean for analyses that depend on ship type?
> 6. Some rows are exact copies of each other: same MMSI, same time and the same content in every column. How many such surplus rows are there? Why do you think the same message appears several times?
> 7. Run the queries in 3.4. What kind of relationship is there between MMSI and IMO in our data? Give one example of an MMSI with several IMO numbers, or an IMO with several MMSI numbers, and suggest an explanation. Did queries A and B give the same number of positions?
>
> **Submit in Canvas:** Answer the quiz for Task 5.
 
---
 
## Part 4 – Visualising AIS tracks in QGIS
 
> 🎯 **Goal for this afternoon:** By the end of the day you can take any vessel from the database and show its track on a map: where it went, how fast, and where the AIS picture has gaps. You will start with one vessel and then build a traffic picture for a whole area.
 
So far you have looked at the data as rows in pgAdmin. A list of positions tells you very little about what a vessel was doing, while a track on a map can show it at a glance: a ferry shuttling between two ports, a fishing vessel working back and forth over a fishing ground, a cargo ship lying still at anchor for hours.
 
### 4.1 Connect QGIS to the database
 
If you imported the contextual data with DB Manager this morning, the connection already exists and you can skip this step.
 
1. In the **Browser** panel, right-click **PostgreSQL** → **New Connection…**
2. Fill in:
   * **Name:** `ingof3205`
   * **Host:** `localhost`
   * **Port:** `5432`
   * **Database:** `ingof3205`
   * **Authentication → Basic:** your PostgreSQL user name and password (tick *Store*)
3. Click **Test Connection**, then **OK**.
Expand the connection in the Browser panel. You should see the schemas `ais_data`, `context_data` and `data_analysis`.
 
> ⚠️ **Do not drag `dynamic_ships` onto the map.** QGIS will try to draw tens of millions of points, and will become very slow or stop responding. Always filter out the data you need first, as we do below.
 
### 4.2 A dark background map
 
AIS tracks stand out best against a dark background. We use the *Dark Matter* map from CARTO. It requires an API key, which you find in Canvas:
 
1. In the **Browser** panel, right-click **XYZ Tiles** → **New Connection…**
2. Fill in:
   * **Name:** `CARTO Dark Matter`
   * **URL:** `https://basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png?key=<API key>`
     (replace `<API key>` with the key from Canvas, without the `< >`)
3. Click **OK**, and double-click the new entry to add it to the map.
If the map shows an "API key required" watermark, part of the key is missing from the URL. The key is for use in this course only: do not share it outside the class.
 
> 💡 **Alternative without a key:** Esri's dark grey basemap. Use the same steps, with the name `Esri Dark Gray` and the URL `https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`. Note that `{y}` and `{x}` are in the opposite order of the CARTO URL.
 
> 💡 **No internet?** Set a dark background colour instead: *Project → Properties → General → Background color*, choose a very dark grey or blue, and add the coastline from the contextual data on top.
 
### 4.3 Choose a vessel
 
Find the 20 vessels with the most positions on 22 October 2025, together with their speed and name. The ship names are looked up for the 20 vessels in the result only, not for every vessel in the database:
 
```sql
WITH top AS (
  SELECT mmsi,
         count(*) AS positions,
         round((avg(speed) FILTER (WHERE speed < 102.3))::numeric, 1) AS avg_speed,
         max(speed) FILTER (WHERE speed < 102.3) AS max_speed
  FROM ais_data.dynamic_ships
  WHERE timestamp_utc >= '2025-10-22'
    AND timestamp_utc <  '2025-10-23'
  GROUP BY mmsi
  ORDER BY positions DESC
  LIMIT 20
)
SELECT top.mmsi, top.positions, top.avg_speed, top.max_speed, n.shipname
FROM top
LEFT JOIN LATERAL (
  SELECT shipname
  FROM ais_data.static_ships
  WHERE sourcemmsi = top.mmsi
    AND trim(shipname) <> ''
  ORDER BY timestamp_utc DESC
  LIMIT 1
) n ON true
ORDER BY top.positions DESC;
```
 
> 🔍 **What the query does**
> * `WITH top AS (...)` defines a **CTE** (*Common Table Expression*): a named, temporary result that the rest of the query can use as if it were a table. It only exists while the query runs.
> * Inside the CTE, `WHERE` keeps the positions from 22 October, and `GROUP BY mmsi` collects the positions of each vessel into one group. For each group, `count(*)` counts the positions, and `avg(speed)` and `max(speed)` give the average and highest speed.
> * `FILTER (WHERE speed < 102.3)` makes the average and the maximum use only valid speeds, leaving out the value meaning "not available". `count(*)` has no filter, so it still counts all positions.
> * `round((...)::numeric, 1)` rounds the average to one decimal. `round` with a number of decimals only works on the type `numeric`, so the average is cast with `::numeric` first. The parentheses make sure the cast applies to the whole filtered average.
> * `ORDER BY positions DESC` sorts with the highest number first, and `LIMIT 20` keeps the top 20.
> * `LEFT JOIN LATERAL (...) n ON true` runs the subquery in parentheses **once for each of the 20 rows**. *LATERAL* allows the subquery to use columns from the table before it, here `top.mmsi`. The join condition is inside the subquery, so `ON true` just says "join every row". *LEFT* keeps vessels that have no name, with `NULL` as the name.
> * The subquery finds the newest name that is not empty: `trim()` removes leading and trailing spaces, `<> ''` leaves out empty names, and `ORDER BY timestamp_utc DESC LIMIT 1` picks the newest.
> * The names are looked up in `static_ships` rather than in the view `ships`. The view would be calculated over the whole static table for every lookup, while `static_ships` has an index on `sourcemmsi`.
 
Choose a vessel that is actually moving: one with an `avg_speed` clearly above 0. A ferry, a Hurtigruten ship or a fishing vessel gives a more interesting track than a vessel lying at the quay all day. **Copy its MMSI**: you will use it in place of `<your MMSI>` in the next step.
 
### 4.4 From positions to a track
 
We make three small tables for the chosen vessel: its **positions**, its **track** as one line, and its **segments**, the short lines between each pair of consecutive positions. The segments let us colour the track by speed.
 
```sql
-- 1. All positions for the vessel on 22 October
CREATE TABLE data_analysis.my_vessel_points AS
SELECT id, mmsi, timestamp_utc, speed, course, status, geom
FROM ais_data.dynamic_ships
WHERE mmsi = <your MMSI>
  AND timestamp_utc >= '2025-10-22'
  AND timestamp_utc <  '2025-10-23';
 
ALTER TABLE data_analysis.my_vessel_points ADD PRIMARY KEY (id);
 
-- 2. The track: all positions connected in time order
CREATE TABLE data_analysis.my_vessel_track AS
SELECT mmsi,
       min(timestamp_utc) AS first_seen,
       max(timestamp_utc) AS last_seen,
       count(*)           AS n_positions,
       ST_MakeLine(geom ORDER BY timestamp_utc)::geometry(LineString, 4326) AS geom
FROM data_analysis.my_vessel_points
GROUP BY mmsi;
 
ALTER TABLE data_analysis.my_vessel_track ADD PRIMARY KEY (mmsi);
 
-- 3. Segments: one short line per pair of consecutive positions, with the speed
CREATE TABLE data_analysis.my_vessel_segments AS
SELECT row_number() OVER () AS id, mmsi, t1, t2, speed_knots, geom
FROM (
  SELECT mmsi,
         timestamp_utc               AS t1,
         LEAD(timestamp_utc) OVER w  AS t2,
         NULLIF(speed, 102.3)        AS speed_knots,   -- "not available" becomes NULL
         ST_MakeLine(geom, LEAD(geom) OVER w)::geometry(LineString, 4326) AS geom
  FROM data_analysis.my_vessel_points
  WINDOW w AS (ORDER BY timestamp_utc)
) q
WHERE t2 IS NOT NULL;
 
ALTER TABLE data_analysis.my_vessel_segments ADD PRIMARY KEY (id);
```
 
> 🔍 **What the query does**
> * **All three:** `CREATE TABLE ... AS SELECT ...` creates a new table and fills it with the result of the query in one step. The columns get their names and types from the `SELECT`. QGIS needs a **primary key** to handle a table properly, and tables made this way do not get one automatically, so `ALTER TABLE ... ADD PRIMARY KEY (...)` adds it afterwards.
> * **1. Positions:** selects the columns we need for one vessel (`WHERE mmsi = ...`) on one day. The composite index on `(mmsi, timestamp_utc)` from 2.4 makes this fast.
> * **2. Track:** `GROUP BY mmsi` collects all the positions into one group, giving one row for the vessel. `min()` and `max()` give the first and last time, and `count(*)` the number of positions. `ST_MakeLine(geom ORDER BY timestamp_utc)` is an **aggregate function**: it connects all the points in the group into one line, in time order. Without `ORDER BY`, the points would be connected in random order and the line would zigzag across the map.
> * **3. Segments:** the inner query (named `q`) goes through the positions in time order. `WINDOW w AS (ORDER BY timestamp_utc)` defines this order once, and `OVER w` uses it. `LEAD(...) OVER w` fetches the value from the **next** row, so `ST_MakeLine(geom, LEAD(geom) OVER w)` makes a line from each position to the next. `NULLIF(speed, 102.3)` turns "not available" into `NULL`. You will use the same technique on Thursday to detect stops.
> * In the outer query, `WHERE t2 IS NOT NULL` removes the last position, which has no next position. `row_number() OVER ()` numbers the rows 1, 2, 3 … to give each segment an `id`.
> * `::geometry(LineString, 4326)` tells PostGIS (and QGIS) exactly what kind of geometry the column holds.
 
> 💡 **Tip: Use a view if you will change vessel often.** With `CREATE VIEW` instead of `CREATE TABLE`, the map updates when you change the MMSI in the view. But a view is recalculated every time QGIS redraws the map, so it can be slow on large data.
 
### 4.5 Style the track
 
Add the three tables to the map from the Browser panel (*PostgreSQL → ingof3205 → data_analysis*). Put the dark background at the bottom of the *Layers* panel.
 
**The track with a glow effect**
 
1. Right-click `my_vessel_track` → **Properties** → **Symbology**.
2. Click **Simple Line**, choose a bright colour (e.g. cyan `#00e5ff`) and set the **Stroke width** to `0.4` mm.
3. Tick **Draw effects** at the bottom, and click the star icon next to it.
4. Tick **Outer Glow**, set the **Spread** to about `1.5` mm and the **Opacity** to about `50 %`. Click **OK**.
**The segments coloured by speed**
 
1. Open the **Symbology** of `my_vessel_segments`, and change *Single Symbol* to **Graduated**.
2. **Value:** `speed_knots`, **Color ramp:** *Plasma* (or another ramp that is bright at the top end), **Mode:** *Equal Interval* or *Natural Breaks*, **Classes:** 5. Click **Classify**.
3. Set the line width to `0.6` mm. Segments with no speed (`NULL`) are not drawn, so you will see gaps where the speed was not available.
**Start and end**
 
Style `my_vessel_points` as small, faint dots (e.g. white, size `0.8` mm, opacity 40 %). Then add two rules (*Rule-based* symbology) to mark the first and last position with larger symbols:
 
* Start: `"timestamp_utc" = minimum("timestamp_utc")`
* End: `"timestamp_utc" = maximum("timestamp_utc")`
> 🔍 **What the expressions do**
> * These are **QGIS expressions**, not SQL, but they work in a similar way. Each rule is tested for every point, and the symbol is used where the rule is true.
> * `minimum("timestamp_utc")` and `maximum("timestamp_utc")` are aggregate functions in QGIS: they return the earliest and latest time in the whole layer. The rule is therefore only true for the first and the last position.
 
**Labels with the time**
 
Label the points with the time, but only every hour, so the map does not get cluttered. In **Labels** → *Single Labels*, use this expression as the value:
 
```text
format_date("timestamp_utc", 'HH:mm')
```
 
and under **Rendering → Show label**, set the data-defined value (the ε button) to:
 
```text
minute("timestamp_utc") = 0 OR "timestamp_utc" = minimum("timestamp_utc")
```
 
> 🔍 **What the expressions do**
> * `format_date("timestamp_utc", 'HH:mm')` formats the time as hours and minutes, e.g. `14:00`. This is the text of the label.
> * `minute("timestamp_utc")` returns the minutes of the time (0–59). `= 0` is true for positions sent at the full hour.
> * `OR "timestamp_utc" = minimum("timestamp_utc")` also shows the label for the first position, so that the start time is always visible.
 
Not all vessels send a position exactly at the full hour, so you may need to adjust this, e.g. to `minute("timestamp_utc") < 3`.
 
### 4.6 Animate the track
 
QGIS can play the track as an animation:
 
1. Open the **Properties** of `my_vessel_points` → **Temporal**.
2. Tick **Dynamic Temporal Control**, choose **Single Field with Date/Time**, select `timestamp_utc`, and set **Event duration** to `10 minutes`. Tick **Accumulate features over time** if you want the track to build up as it plays.
3. Open the Temporal Controller: *View → Panels → Temporal Controller*.
4. Click the play button (▶). Set the step to e.g. `10 minutes` to adjust the speed.
> **Task 6: The track of one vessel**
> 1. Which vessel did you choose (name, MMSI, ship type and flag state)? Why?
> 2. Make a map of its track on 22 October with a dark background, the segments coloured by speed, the start and end marked, and a title. Export it with *Project → Import/Export → Export Map to Image*.
> 3. Describe in 3–5 sentences what the vessel did during the day. Where did it go, where did it stop, and how did the speed change?
> 4. Look closely at the track. Are there places where the line jumps in a straight line, or crosses land? What could explain this?
>
> **Submit in Canvas:** Your map (PNG) and the answers to questions 1, 3 and 4.
 
### 4.7 The traffic picture around Bjørnøya (extension)
 
One vessel tells a story; all vessels together show the patterns. Bjørnøya lies halfway between mainland Norway and Svalbard, in the middle of rich fishing grounds and the sea routes in and out of the Barents Sea. The query below makes one track for every vessel inside a box around Bjørnøya on 22 October:
 
```sql
CREATE TABLE data_analysis.bjornoya_tracks AS
SELECT mmsi,
       count(*) AS n_positions,
       ST_MakeLine(geom ORDER BY timestamp_utc)::geometry(LineString, 4326) AS geom
FROM ais_data.dynamic_ships
WHERE timestamp_utc >= '2025-10-22'
  AND timestamp_utc <  '2025-10-23'
  AND geom && ST_MakeEnvelope(16.0, 73.8, 22.0, 75.0, 4326)  -- box: lon 16–22, lat 73.8–75.0
GROUP BY mmsi
HAVING count(*) > 1;   -- a line needs at least two points
 
ALTER TABLE data_analysis.bjornoya_tracks ADD PRIMARY KEY (mmsi);
```
 
> 🔍 **What the query does**
> * `ST_MakeEnvelope(16.0, 73.8, 22.0, 75.0, 4326)` creates a rectangle from the minimum and maximum longitude and latitude (`xmin, ymin, xmax, ymax`) in the coordinate system 4326. Note that the box is not square on the ground: at 74°N one degree of longitude is only about 30 km, while one degree of latitude is about 111 km. The box is therefore about 180 km wide and 130 km high.
> * `geom && ...` tests whether the bounding box of each position overlaps the rectangle. For points, this is the same as "the point lies inside the rectangle". `&&` uses the GiST index directly, which makes it a fast way to cut out an area.
> * `GROUP BY mmsi` with `ST_MakeLine(geom ORDER BY timestamp_utc)` makes one line per vessel, in the same way as the track in 4.4.
> * `HAVING count(*) > 1` leaves out vessels with only one position inside the box, since a line needs at least two points.
 
Style it to show the traffic density:
 
1. **Simple Line**, a bright colour, **Stroke width** `0.2` mm, **Opacity** about 30 %.
2. Under **Layer Rendering** at the bottom of the Symbology tab, set **Blending mode** to **Addition**. Where many tracks overlap, the colours add up and the main shipping lanes light up.
> 🔎 **Straight lines across the map.** A vessel that leaves the box and comes back later, or that is out of AIS coverage for a while, gets a long straight line between the last and the next position. You can split each track wherever there is a gap of more than 30 minutes:
 
```sql
CREATE TABLE data_analysis.bjornoya_tracks_split AS
WITH p AS (
  SELECT mmsi, timestamp_utc, geom,
         CASE WHEN timestamp_utc - LAG(timestamp_utc) OVER w > interval '30 minutes'
              THEN 1 ELSE 0 END AS new_part        -- 1 where a new part begins
  FROM ais_data.dynamic_ships
  WHERE timestamp_utc >= '2025-10-22'
    AND timestamp_utc <  '2025-10-23'
    AND geom && ST_MakeEnvelope(16.0, 73.8, 22.0, 75.0, 4326)
  WINDOW w AS (PARTITION BY mmsi ORDER BY timestamp_utc)
), parts AS (
  SELECT *, sum(new_part) OVER (PARTITION BY mmsi ORDER BY timestamp_utc) AS part
  FROM p                                           -- running sum = part number
)
SELECT row_number() OVER () AS id, mmsi, part,
       ST_MakeLine(geom ORDER BY timestamp_utc)::geometry(LineString, 4326) AS geom
FROM parts
GROUP BY mmsi, part
HAVING count(*) > 1;
 
ALTER TABLE data_analysis.bjornoya_tracks_split ADD PRIMARY KEY (id);
```
 
> 🔍 **What the query does**
> * The query is built in three steps. The first two are CTEs (`WITH p AS ...`, `parts AS ...`), each building on the one before.
> * **p:** For each position, `LAG(timestamp_utc) OVER w` fetches the time of the **previous** position of the same vessel (`PARTITION BY mmsi` restarts for each vessel, `ORDER BY timestamp_utc` sorts by time). Subtracting two times gives an `interval`. `CASE WHEN ... > interval '30 minutes' THEN 1 ELSE 0 END` gives `new_part` the value 1 where a gap of more than 30 minutes begins a new part, and 0 otherwise.
> * **parts:** `sum(new_part) OVER (PARTITION BY mmsi ORDER BY timestamp_utc)` is a **running sum**: for each position, it adds up all the `new_part` values so far for that vessel. The result is 0 for the first part, 1 after the first gap, 2 after the second, and so on: a part number.
> * **Final step:** `GROUP BY mmsi, part` makes one line per vessel **and** part, so the line is broken at each gap. `row_number() OVER ()` gives each line an `id`.
 
> **Task 6 (extension):** Make a traffic map of the area around Bjørnøya on 22 October. Where are the main shipping lanes, and where are the fishing vessels working? Compare the split and the unsplit tracks: what do the long straight lines in the unsplit version tell you about the AIS coverage? Add the map and 3–5 sentences to your Task 6 submission.
 
---
 
## 5.1–5.4 Spatial queries and the shadow fleet
 
> 🎯 **Goal for Thursday:** Your database is ready, and you can show the results on a map. From here on you will use it to answer questions about what vessels are actually doing: who is close to critical infrastructure, where vessels stop, and when they disappear from AIS. Remember from Task 5 that the data can be wrong, and sometimes deliberately so. By the end of the day you should be ready for Iron Foxes.
 
### 5.1 Spatial relationships
 
Spatial queries test how geometries relate to each other: does a vessel position lie inside an area, does a track cross a cable, how far is a ship from a platform? PostGIS follows the OGC *Simple Features* standard and supports a large set of such functions. They work between any combination of points, lines and polygons, **as long as the geometries are in the same coordinate system (CRS)**.
 
**Functions that test a relationship** (return `true` or `false`):
 
| Function | True when … |
|---|---|
| `ST_Intersects(a, b)` | a and b share at least one point |
| `ST_Disjoint(a, b)` | a and b share no points (the opposite of `ST_Intersects`) |
| `ST_Within(a, b)` | a lies completely inside b |
| `ST_Contains(a, b)` | b lies completely inside a |
| `ST_Touches(a, b)` | a and b touch at the boundary, but their interiors do not overlap |
| `ST_Crosses(a, b)` | a crosses b (e.g. a vessel track crossing a cable) |
| `ST_Overlaps(a, b)` | a and b partly overlap, and are of the same dimension |
| `ST_Equals(a, b)` | a and b are the same geometry |
| `ST_DWithin(a, b, d)` | a and b are within the distance d of each other |
 
**Functions that return a number:** `ST_Distance(a, b)` returns the shortest distance between a and b.
 
**Functions that return a new geometry:** `ST_Buffer` (a zone around a geometry), `ST_ConvexHull` (the smallest convex shape around a set of geometries), and the set operations `ST_Intersection`, `ST_Difference`, `ST_Union` and `ST_SymDifference`.
 
[Figure: spatial relationships]
 
The full list, with drawings of each function, is in the [PostGIS reference](https://postgis.net/docs/reference.html).
 
> 💡 **Tip: `ST_DWithin` rather than `ST_Distance`.** To find everything within 500 m, write `ST_DWithin(a, b, 500)`, not `ST_Distance(a, b) < 500`. `ST_DWithin` can use a spatial index; `ST_Distance` has to calculate the distance to every single row.
 
### 5.2 Spatial indexes
 
In 2.4 you created a **GiST index** on the geometry columns. A GiST index does not store the geometries themselves, but their **bounding boxes**: the smallest rectangle that encloses each geometry.
 
[Figure: bounding boxes]
 
A spatial query with an index is answered in two steps:
 
1. **Filter:** compare the bounding boxes. This is fast, and rules out most geometries straight away.
2. **Refine:** calculate the exact relationship, but only for the few geometries whose boxes overlapped.
Imagine four geometries: a pentagon, a line, a triangle and a circle. Without an index, finding which of them intersect requires comparing every pair, which is six comparisons. With an index, the circle is ruled out because its box overlaps no other box, and the exact (and expensive) calculation is only done twice: between the pentagon and the line, and between the pentagon and the triangle. On tens of millions of positions, this is the difference between seconds and hours.
 
> ⚠️ **The index only helps if the query can use it.** An index on `geom3035` is used when the query compares `geom3035` directly with something. If you transform or cast the indexed column inside the query, for example `ST_Transform(d.geom3035, 4326)` or `d.geom::geography`, the index cannot be used. Transform the *small* table instead, and leave the large table's column untouched.
 
### 5.3 Example: all Russian-flagged vessels
 
With the country code in place, we can select all positions from vessels with a given flag state. Russia has the MID 273:
 
```sql
CREATE TABLE data_analysis.russian_vessels AS
SELECT d.*
FROM ais_data.dynamic_ships d
WHERE d.mmsi IN (
  SELECT sourcemmsi FROM ais_data.ships WHERE cnty_code = 273
);
```
 
> 🔍 **What the query does**
> * `CREATE TABLE data_analysis.russian_vessels AS SELECT ...` creates a new table in the schema `data_analysis` and fills it with the result of the query.
> * `SELECT d.*` takes all columns from `dynamic_ships` (`d` is an alias for the table).
> * The subquery in parentheses produces a list of all MMSI numbers in the view `ships` with country code 273 (Russia). `d.mmsi IN (...)` keeps the positions whose MMSI is in the list.
 
> ⚠️ **Watch out for duplicates.** It is tempting to write `JOIN ais_data.ships s ON d.mmsi = s.sourcemmsi`. But the view can contain several rows for the same MMSI, and a join would then copy every position once for each of those rows (see 3.4 and your answer to Task 5, question 7). Using `IN (...)` only asks *whether* the MMSI is in the list, so each position appears exactly once.
 
### 5.4 The shadow fleet
 
> **Task 7: The shadow fleet**
> Create a table or materialized view in the schema `data_analysis` containing all AIS positions from vessels on the EU sanctions list. You will need to combine `context_data.eudesignated` (IMO numbers), `ais_data.ships` (IMO-to-MMSI mapping) and `ais_data.dynamic_ships` (positions).
>
> **Submit in the Canvas text box:**
> 1. Your SQL statement
> 2. How many sanctioned vessels you found, and how many positions they have
> 3. A short justification (3–5 sentences) for choosing a table or a materialized view
> 4. A short reflection: which shadow-fleet vessels might your query **miss**, and why?
 
---
 
## 5.5 Who was close to Goliat?
 
The query below finds vessels that were moving slowly (under 2 knots) within 500 m of the Goliat platform in the Barents Sea on 15 October 2025, and how long each of them stayed there.
 
```sql
SELECT q3.mmsi,
       q3.facname,
       s.shipname,
       s.shiptype_text,
       q3.first_seen,
       q3.last_seen,
       q3.last_seen - q3.first_seen AS duration
FROM (
  SELECT o.facname,
         d.mmsi,
         min(d.timestamp_utc) AS first_seen,
         max(d.timestamp_utc) AS last_seen
  FROM context_data.oil_gas_infrastructure o
  JOIN ais_data.dynamic_ships d
    ON  d.speed < 2
    AND d.timestamp_utc >= '2025-10-15'
    AND d.timestamp_utc <  '2025-10-16'
    AND ST_DWithin(d.geom3035, ST_Transform(o.geom, 3035), 500)  -- 500 metres
  WHERE o.facname ILIKE '%goliat%'   -- matches the name regardless of case and suffix
  GROUP BY o.facname, d.mmsi
) q3
LEFT JOIN LATERAL (
  -- the most recently reported name and ship type for this MMSI,
  -- taken from different rows if necessary (class B vessels, see 3.3)
  SELECT
    (array_agg(shipname ORDER BY last_seen DESC)
       FILTER (WHERE trim(shipname) <> ''))[1]  AS shipname,
    (array_agg(shiptype_text ORDER BY last_seen DESC)
       FILTER (WHERE shiptype <> 0))[1]         AS shiptype_text
  FROM ais_data.ships
  WHERE sourcemmsi = q3.mmsi
) s ON true;
```
 
> 🔍 **What the query does**
> * The query is easiest to read from the inside out. The **inner query** (in parentheses, named `q3`) finds the vessels; the **outer query** adds names and calculates the duration.
> * **Inner query:** `FROM ... oil_gas_infrastructure o JOIN ... dynamic_ships d ON ...` combines the platform with every position that meets **all** the conditions after `ON`: speed under 2 knots, the right day, and within 500 m. `WHERE o.facname ILIKE '%goliat%'` picks the platform. `ILIKE` compares text without regard to upper and lower case, and `%` means "any text", so the name only has to contain *goliat*.
> * `ST_DWithin(d.geom3035, ST_Transform(o.geom, 3035), 500)` is true when the position is within 500 units of the platform. In EPSG:3035 the unit is metres. The platform (one row) is transformed to 3035, while the tens of millions of vessel positions are left as they are, so the index on `geom3035` can be used.
> * The time filter is written as a range (`>=` and `<`), so the index on `timestamp_utc` can be used. You saw why in Task 3.
> * `GROUP BY o.facname, d.mmsi` gives one row per vessel. `min()` and `max()` give the first and last time the vessel was inside the zone.
> * **Outer query:** `q3.last_seen - q3.first_seen` subtracts two times, which gives the duration as an `interval` (e.g. `02:15:00`). Note that this is the time from the first to the last position inside the zone; the vessel may have left and come back in between.
> * `LEFT JOIN LATERAL (...) s ON true` runs the subquery once for each vessel, with that vessel's MMSI (`q3.mmsi`), and returns **one** row per MMSI. A plain join could return several rows per vessel, for the same reason as in 5.3.
> * In the subquery, `array_agg(shipname ORDER BY last_seen DESC)` collects all the names of the vessel into a list, newest first. `FILTER (WHERE ...)` leaves out empty names and unknown ship types, and `[1]` picks the first element of the list. This way a class B vessel gets both its name and its ship type, even when they come from different rows.
 
To draw the 500 m zone around the platform, make a buffer. The buffer is made in EPSG:3035, so that the distance is in metres:
 
```sql
CREATE TABLE data_analysis.goliat_buffer AS
SELECT facname,
       ST_Buffer(ST_Transform(geom, 3035), 500)::geometry(Polygon, 3035) AS geom
FROM context_data.oil_gas_infrastructure
WHERE facname ILIKE '%goliat%';
 
ALTER TABLE data_analysis.goliat_buffer ADD COLUMN id serial PRIMARY KEY;
```
 
> 🔍 **What the query does**
> * `ST_Transform(geom, 3035)` converts the platform position to EPSG:3035, so that distances are in metres.
> * `ST_Buffer(..., 500)` makes a polygon covering everything within 500 m of the geometry: for a point, a circle with a radius of 500 m.
> * `::geometry(Polygon, 3035)` states the geometry type and coordinate system of the column, for QGIS.
> * `ADD COLUMN id serial PRIMARY KEY` adds a numbered primary key, so that QGIS can handle the table.
 
The buffer is in EPSG:3035 and the track in EPSG:4326. That is not a problem for the map: QGIS reprojects layers on the fly.
 
> **Task 8: Goliat**
> 1. Which vessel was close to Goliat on 15 October? What type of ship is it, and for how long was it within 500 m?
> 2. Visualise the vessel's movements during the whole of 15 October in QGIS, together with the platform and a 500 m buffer around it. Use the same technique as in Part 4 to make the track.
> 3. Based on the ship type and the movement pattern: what do you think the vessel was doing there?
>
> **Submit in Canvas:** Short answers to the questions, and a screenshot of your map.
 
---
 
## 5.6 Stops near critical infrastructure
 
Where a vessel stops says a lot about what it is doing. A vessel that lies still over a subsea cable for hours, far from any port, is more interesting than one that is moored at the quay.
 
A **stop** is a sequence of positions where the speed is zero or below a low threshold. To find stops, we first build a table of **segments**: every pair of consecutive positions for the same vessel, connected by a line. From the segments we can then find where a vessel slows down (a stop begins) and where it speeds up again (the stop ends).
 
> ⚠️ **Choose your vessels.** Running the stop detection on all positions in the dataset takes a very long time, and most of the stops you find will be vessels lying in port. In the examples below we use the Russian-flagged vessels from 5.3 (`data_analysis.russian_vessels`). You can replace this with your shadow fleet from Task 7, or with another selection you can justify.
 
#### Step 1: Segments
 
```sql
CREATE INDEX idx_russian_vessels_mmsi_t
  ON data_analysis.russian_vessels (mmsi, timestamp_utc);
 
CREATE TABLE data_analysis.segments AS
SELECT mmsi,
       t1, t2,                                   -- start and end time
       speed1, speed2,                           -- speed at start and end (knots)
       p1, p2,                                   -- start and end position (EPSG:3035)
       ST_MakeLine(p1, p2)              AS segment,
       ST_Distance(p1, p2)              AS distance_m,
       extract(epoch FROM (t2 - t1))    AS duration_s,
       CASE WHEN t2 > t1
            THEN ST_Distance(p1, p2) / extract(epoch FROM (t2 - t1))
       END                              AS speed_m_s  -- calculated speed (m/s)
FROM (
  SELECT mmsi,
         timestamp_utc               AS t1,
         LEAD(timestamp_utc) OVER w  AS t2,
         speed                       AS speed1,
         LEAD(speed) OVER w          AS speed2,
         geom3035                    AS p1,
         LEAD(geom3035) OVER w       AS p2
  FROM data_analysis.russian_vessels
  WINDOW w AS (PARTITION BY mmsi ORDER BY timestamp_utc)
) q
WHERE t2 IS NOT NULL;   -- the last position of each vessel has no next position
 
CREATE INDEX idx_segments_speed ON data_analysis.segments (speed1, speed2);
```
 
> 🔍 **What the query does**
> * The first index, on `(mmsi, timestamp_utc)`, makes it fast to go through the positions of each vessel in time order, which is what the query below does.
> * **The inner query** (named `q`) goes through the positions. `WINDOW w AS (PARTITION BY mmsi ORDER BY timestamp_utc)` defines how: `PARTITION BY mmsi` divides the positions into one group per vessel, and `ORDER BY timestamp_utc` sorts each group by time. `LEAD(...) OVER w` then fetches the value from the **next** row in the same group. This makes sure that "next" means the next position of **the same vessel**, so a segment never connects the last position of one vessel with the first position of another.
> * Each row in `q` thus has a start (`t1`, `speed1`, `p1`) and an end (`t2`, `speed2`, `p2`).
> * **The outer query** calculates the segment: `ST_MakeLine(p1, p2)` is the line, `ST_Distance(p1, p2)` the distance in metres (since the points are in EPSG:3035), and `extract(epoch FROM (t2 - t1))` the duration in seconds (`epoch` converts an interval to seconds).
> * `CASE WHEN t2 > t1 THEN ... END` calculates the speed only when time has passed between the two positions. Two positions with the same timestamp would otherwise mean dividing by zero. Without `ELSE`, the value is `NULL`.
> * `WHERE t2 IS NOT NULL` removes the last position of each vessel, which has no next position.
> * The last index, on `(speed1, speed2)`, makes the next step fast, since it searches for segments by speed.
 
> 🧭 **Two speeds.** `speed1` and `speed2` are the speeds reported by the vessel itself, in **knots**. `speed_m_s` is calculated by us from the distance and time between two positions, in **metres per second** (1 knot ≈ 0.514 m/s). If the two disagree badly, for example a reported speed of 10 knots but a calculated speed of 400 m/s, something is wrong: a GPS error, a shared MMSI, or a manipulated position. The segments table is therefore also a good tool for finding errors.
 
#### Step 2: Start and end of stops
 
A stop **begins** where a segment goes from moving to still (speed above the threshold at the start, below at the end), and **ends** where a segment goes from still to moving.
 
```sql
-- Stops begin: the vessel slows down below the threshold
CREATE TABLE data_analysis.stop_begin AS
SELECT mmsi,
       t2 AS t_begin,
       p2 AS geom3035          -- where the stop begins
FROM data_analysis.segments
WHERE speed1 > 0.5 AND speed2 <= 0.5;   -- threshold: 0.5 knots
 
CREATE INDEX idx_stop_begin_mmsi_t ON data_analysis.stop_begin (mmsi, t_begin);
 
-- Stops end: the vessel speeds up above the threshold
CREATE TABLE data_analysis.stop_end AS
SELECT mmsi,
       t1 AS t_end
FROM data_analysis.segments
WHERE speed1 <= 0.5 AND speed2 > 0.5;
 
CREATE INDEX idx_stop_end_mmsi_t ON data_analysis.stop_end (mmsi, t_end);
```
 
> 🔍 **What the query does**
> * `stop_begin` picks out the segments where the speed goes from above the threshold (`speed1 > 0.5`) to at or below it (`speed2 <= 0.5`): the vessel slows down and stops. The stop begins at the end of the segment, so the table stores `t2` and `p2`.
> * `stop_end` does the opposite: the speed goes from at or below the threshold to above it. The stop ends at the start of that segment, so the table stores `t1`.
> * The indexes on `(mmsi, t_begin)` and `(mmsi, t_end)` make the next step fast, where each beginning is paired with an end for the same vessel.
 
#### Step 3: Pair beginnings and ends
 
For each stop beginning, we find the **first** stop end for the same vessel that comes after it:
 
```sql
CREATE TABLE data_analysis.stops AS
SELECT b.mmsi,
       b.t_begin,
       e.t_end,
       extract(epoch FROM (e.t_end - b.t_begin)) AS duration_s,
       b.geom3035
FROM data_analysis.stop_begin b
JOIN LATERAL (
  SELECT t_end
  FROM data_analysis.stop_end e
  WHERE e.mmsi = b.mmsi
    AND e.t_end >= b.t_begin
  ORDER BY e.t_end
  LIMIT 1
) e ON true;
```
 
> 🔍 **What the query does**
> * For each row in `stop_begin` (alias `b`), the `LATERAL` subquery searches `stop_end` for an end for **the same vessel** (`e.mmsi = b.mmsi`) that comes **after** the beginning (`e.t_end >= b.t_begin`).
> * `ORDER BY e.t_end LIMIT 1` picks the **first** such end, which is the end of this particular stop and not of a later one.
> * `JOIN LATERAL ... ON true` (not *LEFT*) keeps only the beginnings that have an end. The condition is inside the subquery, so `ON true` just joins the rows.
> * `extract(epoch FROM (e.t_end - b.t_begin))` gives the duration of the stop in seconds. Divide by 3600 to get hours.
 
Stops that never end within the dataset (the vessel was still lying still at the end of October) disappear in this join. Think about whether that matters for your analysis.
 
> **Task 9: Stops near critical infrastructure**
> 1. Run the stop detection on your selection of vessels. How many stops did you find, and how long was the longest?
> 2. Find the stops that lasted **more than one hour** and lie **within 2 km of a subsea cable or pipeline**. (Hint: `ST_DWithin`, and remember which table to transform.)
> 3. Visualise these stops in QGIS together with the cables and pipelines.
> 4. The examples use a threshold of 0.5 knots. Run the stop detection again with 0.1 knots. What changes, and why? Which threshold would you choose?
> 5. Pick one of the stops and assess it: is it suspicious? What other explanations could there be (anchoring while waiting for port, weather, fishing, repair work)? Does the navigational status the vessel reported during the stop (`status`) support or contradict your interpretation? What other data would you need to be more certain?
>
> **Submit in the Canvas text box:** Your SQL for question 2, the answers to questions 1, 4 and 5 (3–5 sentences each), and a screenshot of your map.
 
---
 
## 5.7 Going dark (advanced)
 
This is the last part before Iron Foxes on Friday. The task is **advanced** and optional: do it if you have time left after Task 9.
 
A vessel that switches off its AIS transponder disappears from the picture. In the segments table, this shows up as a segment with a **long duration**: a long time passed between two positions.
 
> **Task 10 (advanced): Gaps in the AIS picture**
> 1. Find segments in your selection with a duration of more than 2 hours. Where do the gaps start and end?
> 2. Not every gap means that AIS was switched off. The coverage of Kystverket's AIS network is limited far from the coast, and the dataset does not include all vessel types (see the limitations of the dataset). How can you distinguish a gap caused by poor coverage from a vessel deliberately going dark? Use the distance and the calculated speed over the gap in your reasoning, and look at the column `data_source`: were the positions before and after the gap received in the same way?
> 3. Visualise the most interesting gaps in QGIS. (Hint: the segments table already contains a line for each gap.)
>
> **Submit in the Canvas text box:** Your SQL, a screenshot of your map, and a short reflection (5–10 sentences).
 
