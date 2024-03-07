
AIS Data Management: https://meridian.cs.dal.ca/wp-content/uploads/2020/11/AIS.pdf
Anita Graser POSTGIS: https://anitagraser.com/tag/postgis/ 
PostGIS-SpatioTemporal (Anita Graser) https://github.com/anitagraser/postgis-spatiotemporal/blob/master/plpgsql_detectstops.sql


	
#this file includes some SQL-examples which might help you with your analysis

CREATE DATABASE "ING3209" ;
	
CREATE SCHEMA "ais_data" ;

CREATE EXTENSION postgis;

-- Create table for static data (message 5)

CREATE TABLE ais_data.static_ships(
  callsign text,
  datetime text,
  destination text,
  eta text,
  imo double precision,
  mmsi integer,
  shipname text,
  shiptype integer,
  shiptype_text text,
  type integer,
  id bigserial,
  CONSTRAINT static_ships_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

-- Copy from CSV-files into database
Use the import_AIS_postgres.py


--create country codes table
CREATE TABLE context_data.cnty_codes (
    digit INTEGER PRIMARY KEY,
    country VARCHAR(255)
);


--add country code in static ships
ALTER TABLE ais_data.static_ships ADD COLUMN cnty text;
ALTER TABLE ais_data.static_ships ADD COLUMN cnty_code integer;

UPDATE ais_data.static_ships
SET cnty = cnty_codes.country,
    cnty_code = cnty_codes.digit
FROM context_data.cnty_codes
WHERE SUBSTRING(static_ships.mmsi::text FROM 1 FOR 3)::integer = cnty_codes.digit;


--create view ships 
CREATE OR REPLACE VIEW ais_data.ships AS SELECT
  sourcemmsi,
  imo,
  callsign,
  shipname,
  shiptype,
  shiptype_text,
  cnty,
  cnty_code
FROM ais_data.static_ships
GROUP BY mmsi,imo,callsign,shipname,shiptype, shiptype_text,cnty, cnty_code ;

-- SQL query that shows how many MMSI numbers are used more than once from the table ais_data.ships and include both mmsi and shipname in the result
SELECT s1.MMSI, s1.shipname
FROM ais_data.ships s1
INNER JOIN (
  SELECT MMSI
  FROM ais_data.ships
  GROUP BY MMSI
  HAVING COUNT(*) > 1
) s2 ON s1.MMSI = s2.MMSI;

-- SQL query that shows how many MMSI numbers and shipname are used twice are used more than once from the table ais_data.ships
SELECT MMSI, COUNT(*)
FROM ais_data.ships
GROUP BY MMSI
HAVING COUNT(*) > 1;

-- How many ships have null, empty or space filled shipname ?
SELECT COUNT(*), mmsi
FROM ais_data.ships
WHERE shipname IS NULL OR TRIM(shipname) = ''
GROUP BY shipname, mmsi;

--Create vessel info function
CREATE OR REPLACE FUNCTION get_vessel_info_v3 (
  input_mmsi integer
)
RETURNS text AS $$
DECLARE
  vessel_imo integer;
  vessel_name text;
  vessel_shiptype integer;
  vessel_shiptype_text text;
  country text;
BEGIN
  SELECT shipname, imo, shiptype, shiptype_text, cnty INTO vessel_name, vessel_imo, vessel_shiptype, vessel_shiptype_text, country
  FROM ais_data.static_ships
  WHERE mmsi = input_mmsi
  LIMIT 1;
  
  IF vessel_name IS NOT NULL AND vessel_imo IS NOT NULL THEN
    RETURN '[' || vessel_imo || '] ' || vessel_name || ', Type: ' || vessel_shiptype || ' (' || vessel_shiptype_text || '), Country: ' || country || ';';
  ELSE
    RETURN 'Vessel information not found.';
  END IF;
END;
$$ LANGUAGE plpgsql;




-- Create table that contains the moving data
CREATE TABLE ais_data.dynamic_ships(
  course double precision,
  datetime text,
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

-- Copy from CSV-files into database
Use the import_AIS_postgres.py
# copy ais_data.dynamic_ships (course, datetime, heading, lat, lon, mmsi, speed, status_text, turn, type) FROM '/Users/luggerud/Desktop/ais-pos/2023-02-09.csv' DELIMITER ',' CSV HEADER QUOTE '\"' NULL ' ' ESCAPE '''';""

-- make data temporal
ALTER TABLE ais_data.dynamic_ships ADD COLUMN t timestamp without time zone;
UPDATE ais_data.dynamic_ships SET t = to_timestamp(datetime,'YYYY-MM-DD HH24:MI:SS.MS');

-- create index on the time column
CREATE INDEX idx_dynamic_ships_time
ON ais_data.dynamic_ships 
USING btree (t) ;

-- query returned successfully in 30 min 43 secs.

--create index on mmsi column
CREATE INDEX idx_dynamic_ships_mmsi
ON ais_data.dynamic_ships
USING btree (mmsi) ;
Query returned successfully in 2 min 10 secs

--find max and min t from dynamic_ships
SELECT min(t) , max(t) FROM ais_data.dynamic_ships ;

--make data geograpic (consider transforming the coordinates in to 3035 to save time)
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom geometry(Point,4326);
UPDATE ais_data.dynamic_ships
SET geom=ST_SetSRID (ST_MakePoint(lon,lat),4326) ;

--Index dynamic ships
CREATE INDEX idx_dynamic_ships_geom
ON ais_data.dynamic_ships
USING GiST (geom);
Query complete 01:19:35.764

--legge til felt for ETRS-89 geometri i dynamic ships
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom3035 geometry(Point ,3035);

--Copy data from geom and transform them into 3035
UPDATE ais_data.dynamic_ships
SET geom3035 = ST_Transform(geom, 3035)
WHERE geom IS NOT NULL;
	
---Index geom3035
CREATE INDEX idx_dynamic_ships_geom3035
ON ais_data.dynamic_ships
USING GiST (geom3035);

Query returned successfully in 3 hr 35 min

-- create a table holding the suspicious vessels (copy data from suspicious_vessels.csv)
CREATE TABLE ais_data.susp_vessels AS
SELECT *
FROM ais_data.dynamic_ships
WHERE MMSI IN (
    273355170, 273355040, 273338310, 273118000, 273112800,
    273131200, 217114000, 273116000, 273333440, 273138300,
    273317430, 273115700, 273114000, 273315200, 273331830,
    273325210, 273113600, 273333020, 273453700, 273133800,
    273243700, 273340570, 273330620, 273454600, 273452600,
    273113800, 273386130, 273363000, 273383350, 273114600,
    273349820, 273148810, 273399790, 273350540, 273380520,
    273357360, 273131200, 273113600, 273399790, 273350540,
    273380520, 273357360
);


--Select all the military vessels 
SELECT DISTINCT MMSI
FROM ais_data.static_ships
WHERE shiptype = 35
limit 1000
;

--Create table mil vessels based on the result from the query above
CREATE VIEW ais_data.military_vessels AS
SELECT *
FROM ais_data.dynamic_ships
WHERE MMSI IN (
    205207000, 211210180, 211210190, 211210280, 211211160, 211211760, 211901000, 
    211909000, 211920000, 211927000, 211931000, 219000092, 219000161, 219000177, 
    219000181, 219000185, 219000192, 219000416, 219000469, 219000553, 219002066, 
    219007679, 219103000, 219104000, 219105000, 219158000, 219263000, 219517000, 
    219522000, 219524000, 219525000, 220429000, 220431000, 220436000, 224457000, 
    225988520, 227999100, 232002833, 232691000, 234627000, 235053411, 235069661, 
    235070237, 235070238, 235109338, 244159000, 244173000, 244251000, 244465000, 
    245047000, 245330000, 245344000, 245365000, 245965000, 257001000, 257019000, 
    257036200, 257069500, 257086200, 257092200, 257111010, 257148200, 257149200, 
    257156200, 257157200, 257158200, 257159200, 257218500, 257446000, 257985000, 
    258072000, 258242500, 258314500, 258592000, 259010000, 259014000, 259015000, 
    259019000, 259026000, 259031000, 259041000, 259042000, 259043000, 259045000, 
    259049000, 259119000, 261283000, 263020000, 276700000, 338806000, 338846000, 
    419100133
);

-- Create table containg only Russian ships
CREATE TABLE ais_data.russianships AS
SELECT *
FROM ais_data.dynamic_ships
WHERE SUBSTRING(d.mmsi::text, 1, 3) = '273';

-- Create table with Chinese vessels
CREATE TABLE ais_data.chinese_vessels AS
SELECT *
FROM ais_data.dynamic_ships
WHERE SUBSTRING(mmsi::text, 1, 3) = '412' OR
SUBSTRING(mmsi::text, 1, 3) = '413' OR
SUBSTRING(mmsi::text, 1, 3) = '414'
;




-- Select susp_vessels within 500 m of oil and gas facilities
SELECT "facilityName", mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
    SELECT 
        "facilityName", -- Facility name
        mmsi, -- MMSI identifier of the ship
        min(t) as min_t, -- First timestamp of a not moving position
        max(t) as max_t  -- Last timestamp of a not moving position
    FROM context_data."OilAndGasOffshoreConstructions" as q1 -- Facility location
    INNER JOIN ais_data.susp_vessels as q2 -- Ship AIS positions
    ON (
        q2.t >= '2023-01-04 00:00:00' AND 
        q2.t < '2023-03-20 00:00:00' AND -- Between January 4 and January 6, 2023
        ST_dWithin(q1.geom, q2.geom3035, 1000) -- Ship position within 500m of the facility location
    )
    GROUP BY "facilityName", mmsi
) as q3
LEFT JOIN ais_data.ships as q4 -- Ship names
ON (
    q3.mmsi = q4.sourcemmsi
);


-- Select all vessels within 1000 m of oil and gas facilities	
SELECT "facilityName", mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
    SELECT 
        "facilityName", -- Facility name
        mmsi, -- MMSI identifier of the ship
        min(t) as min_t, -- First timestamp of a not moving position
        max(t) as max_t  -- Last timestamp of a not moving position
    FROM context_data."OilAndGasOffshoreConstructions" as q1 -- Facility location
    INNER JOIN ais_data.dynamic_ships as q2 -- Ship AIS positions
    ON (
        q2.speed < 2 AND
		q2.t >= '2023-01-04 00:00:00' AND 
        q2.t < '2023-03-30 00:00:00' AND -- Between January 4 and January 6, 2023
        ST_dWithin(q1.geom, q2.geom3035, 1000) -- Ship position within 500m of the facility location
    )
    GROUP BY "facilityName", mmsi
) as q3
LEFT JOIN ais_data.ships as q4 -- Ship names
ON (
    q3.mmsi = q4.sourcemmsi
);
Query complete 01:10:20.864 - 3660 rows
	
-- Select all russian vessels within 5000 m of Forsvaret installations	
SELECT "HER_ETABNA", mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
    SELECT 
        "HER_ETABNA", -- Facility name
        mmsi, -- MMSI identifier of the ship
        min(t) as min_t, -- First timestamp of a not moving position
        max(t) as max_t  -- Last timestamp of a not moving position
    FROM context_data."Forsvaret_2024" as q1 -- Facility location
    INNER JOIN ais_data.russianships as q2 -- Ship AIS positions
    ON (
		q2.t >= '2023-01-04 00:00:00' AND 
        q2.t < '2023-03-30 00:00:00' AND -- Between January 4 and January 6, 2023
        ST_dWithin(q1.geom, q2.geom3035, 5000) -- Ship position within 500m of the facility location
    )
    GROUP BY "HER_ETABNA", mmsi
) as q3
LEFT JOIN ais_data.ships as q4 -- Ship names
ON (
    q3.mmsi = q4.sourcemmsi
);


-- Create a table with linesegments from the table mil_vessels
CREATE TABLE mil_vessel_line AS
SELECT
  mmsi, ST_MakeLine(geom3035 ORDER BY t ASC) AS line_geom
FROM
    ais_data."mil_vessel"
GROUP BY
    mmsi;



----SØPPELBØTTE-----
# her legges queries som ikke blir brukt eller ikke fungerer, men som jeg ikke ønsker å slette

--add cnty_code in dynamic ships (for tidkrevende, ble aldri gjort)
ALTER TABLE ais_data.dynamic_ships ADD COLUMN cnty_code integer;
UPDATE ais_data.dynamic_ships
SET cnty_code = cnty_codes.digit
FROM ais_data.cnty_codes
WHERE SUBSTRING(dynamic_ships.mmsi::text FROM 1 FOR 3)::integer = cnty_codes.digit;


--Create table with russian ships which includes (for tidkrevende og maskinen går tom for plass før query er ferdig..)
DROP TABLE IF EXISTS ais_data.russianships;

CREATE TABLE ais_data.russianships AS
SELECT d.*, s.shiptype, 
FROM ais_data.dynamic_ships d
JOIN ais_data.static_ships s ON d.MMSI = s.MMSI
WHERE SUBSTRING(d.mmsi, 1, 3) = '273';



-- SHP2PGSQL - convert from shapefiles to PGSQL-format
/Library/PostgreSQL/15/bin/shp2pgsql -s 4230 -I /Users/luggerud/Downloads/pipLine/pipLine.shp context_data.pipeline > /Users/luggerud/Downloads/pipLine/outputfile.sql

-- Importert it into the database
psql -d ING3209_AIS -U postgres -f /Users/luggerud/Downloads/Energi_0000_Norge_25833_Nettanlegg_PostGIS.sql

--legge til felt for geom3035
ALTER TABLE data_analysis.stops
ALTER COLUMN centr4230 TYPE geometry(Point,3035) USING ST_Transform(centr4230, 3035);

--legge til felt for ETRS-89 geometri i dynamic ships
ALTER TABLE ais_data.dynamic_ships ADD COLUMN geom3035 geometry(Point ,3035);

UPDATE ais_data.dynamic_ships
SET geom3035=ST_Transform(geom,3035);


--endre til ETRS-89 for infrastructure og pipeline
ALTER TABLE context_data.pipeline
ALTER COLUMN geom TYPE geometry(Multilinestring,3035) USING ST_Transform(geom, 3035)
;


--funker ikke (invalid format eller noe)
ALTER TABLE context_data.infrastructure_point
ALTER COLUMN geom TYPE geometry(Point,3035) USING ST_Transform(geom, 3035)
;


--Index infrastructure
CREATE INDEX idx_infrastructure_geom
ON context_data.infrastructure
USING GiST (geom);

--index pipeline
CREATE INDEX idx_pipeline_geom
ON context_data.pipeline
USING GiST (geom);











--SPATIAL QUERY innen 500 meter fra olje og gassledning 10. februar
SELECT pipname, mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
SELECT pipname, mmsi, min(t) as min_t , max(t) as max_t FROM context_data.pipeline as q1
INNER JOIN ais_data.dynamic_ships as q2
ON (
    speed=0
    AND t>='2023-02-10 00:00:00'
    AND t<'2023-02-11 00:00:00'
    AND ST_dWithin(q1.geom,q2.geom4230,100)
    )
GROUP BY pipname, mmsi) as q3
LEFT JOIN ais_data.static_ships as q4 
ON (q3.mmsi=q4.sourcemmsi);

--SPATIAL QUERY innen 500 meter fra olje og gassinfrastruktur 10. februar
SELECT facname, mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
SELECT facname, mmsi, min(t) as min_t , max(t) as max_t FROM context_data.infrastructure as q1
INNER JOIN ais_data.dynamic_ships as q2
ON (
    speed=0
    AND t>='2023-02-10 00:00:00'
    AND t<'2023-02-11 00:00:00'
    AND ST_dWithin(q1.geom,q2::geography.geom4230::geography,500)
    )
GROUP BY facname, mmsi) as q3
LEFT JOIN ais_data.static_ships as q4 
ON (q3.mmsi=q4.sourcemmsi);


-- Query som viser hvor mange skip som har vært innenfor 500 meter av Draugen fra 9. februar til 12. februar, kun et resultat
SELECT DISTINCT ON (mmsi) facname, mmsi, shipname, min_t, max_t, (max_t - min_t) as dur
FROM (
SELECT facname, mmsi, min(t) as min_t , max(t) as max_t FROM context_data.infrastructure as q1
INNER JOIN ais_data.dynamic_ships as q2
ON (
    speed=0
    AND t>='2023-02-09 00:00:00'
    AND t<'2023-02-12 00:00:00'
    AND ST_dWithin(q1.geom::geography,q2.geom4230::geography,500)
    )
WHERE facname = 'DRAUGEN'
GROUP BY facname, mmsi) as q3
LEFT JOIN ais_data.static_ships as q4 
ON (q3.mmsi=q4.sourcemmsi);


-- Count distinct ships in a given time interval (10. februar)
SELECT COUNT(DISTINCT ds.MMSI) AS ship_count, s.shipname
FROM ais_data.dynamic_ships ds
JOIN ais_data.ships s ON ds.MMSI = s.MMSI
WHERE ds.t >= '2023-02-10 00:00:00' AND ds.t < '2023-02-11 00:00:00'
GROUP BY ds.MMSI, s.shipname;

--Svar: 2150

--endre projisering til 4230
select UpdateGeometrySRID('context_data', 'infrastructure', 'geom', 4230) ;


--create voronoi polygons
CREATE TABLE data_analysis.fac_voronoi AS
SELECT idfacility as fac_id, facname as name , geom, voronoi_zone4230
FROM context_data.infrastructure
LEFT JOIN (
SELECT (ST_Dump(ST_VoronoiPolygons(ST_Collect(geom)))).geom as voronoi_zone4230
FROM context_data.infrastructure ) as vp
ON (ST_Within(infrastructure.geom, vp.voronoi_zone4230 ) ) ;

--create index on mmsi and time
CREATE INDEX idx_dynamic_ships_mmsi_t ON ais_data.dynamic_ships USING btree (mmsi,t);

--create index on mmsi and time static data
CREATE INDEX idx_static_ships_mmsi_t ON ais_data.static_ships USING btree (mmsi,t);


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
    geom3035 as p1, -- initial point
    LEAD(geom3035) OVER (ORDER BY mmsi,t) as p2 -- final point
  FROM ais_data.dynamic_ships) as q1
WHERE mmsi=mmsi2; -- filter out different mmsi 


CREATE INDEX idx_segments_speed ON data_analysis.segments USING btree (speed1,speed2) ;

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


--create stops table
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

-- add columns for centroid and number of positions
ALTER TABLE data_analysis.stops ADD COLUMN centr3035 geometry(Point,3035); 
ALTER TABLE data_analysis.stops ADD COLUMN nb_pos integer ;

-- compute the centroid and number of positions
UPDATE data_analysis.stops SET (centr3035, nb_pos) = (
SELECT st_centroid (st_collect(geom3035) ) , -- centroid of a multipoint
 count (*) as nb -- number of points
FROM ais_data.dynamic_ships WHERE mmsi=stops.mmsi AND
t>=stops.t_begin AND t<=stops.t_end ) ; -- timestamp range


-- add columns for distance to centroid
ALTER TABLE data_analysis.stops ADD COLUMN avg_dist_centroid numeric ;
ALTER TABLE data_analysis.stops ADD COLUMN max_dist_centroid numeric ;

-- compute the distance of the position cluster to the centroid 
UPDATE data_analysis.stops
SET (avg_dist_centroid , max_dist_centroid) = (
SELECT avg(d), max(d) FROM (
SELECT st_distance(centr3035,geom3035) as d -- distance to centroid
FROM ais_data.dynamic_ships
WHERE mmsi=stops.mmsi AND
t>=stops.t_begin AND t<=stops.t_end -- timestamp range
 ) as q1);

-- count the number of stops that are at least 5 minutes long and within 10m from centroid
SELECT count (*)
FROM data_analysis.stops
WHERE duration_s >=(5*60) -- 5 minutes long
AND nb_pos>5 -- minimum 5 consecutive positions
AND avg_dist_centroid <=10; -- within 10m from centroid

--Answer: 233 523


-- create index on centroid
CREATE INDEX idx_stops_centroid ON data_analysis.stops USING btree ( centr3035 ) ;

-- transform centroid to ETRS89 EPSG:3035
ALTER TABLE data_analysis.stops
ALTER COLUMN centr4230 TYPE geometry(Point,3035) USING ST_Transform(centr4230, 3035);


-- create table that clusters stops using DBSCAN
CREATE OR REPLACE TABLE data_analysis.cluster_stops AS
SELECT *, ST_ClusterDBSCAN(centr3035, eps := 200, minpoints := 5) OVER ()
AS cid
FROM data_analysis.stops
WHERE duration_s >=60; -- 1 minute long


-- create index
CREATE INDEX idx_stops_centroid_cluster_stops ON data_analysis.cluster_stops USING btree ( centr3035 ) ;

-- create table with cluster stops hulls
CREATE TABLE data_analysis.clusters_stops_hulls AS
SELECT cid, -- cluster id
  ST_ConvexHull(st_collect(centr3035)) AS convex_hull,
  CASE 
    WHEN st_npoints(st_collect(centr3035)) >= 4 THEN ST_ConcaveHull(st_collect(centr3035), 0.75)
    ELSE NULL
  END AS concave_hull,
  ST_MinimumBoundingCircle(st_collect(centr3035)) AS bounding_circle,
  ST_Centroid(st_collect(centr3035)) AS centroid,
  count(*) AS nb_stops, -- number of stops in this cluster ( area )
  sum(nb_pos) AS nb_pos, -- sum of stops in the cluster
  count(DISTINCT mmsi) AS nb_ships, -- num of unique ships
  min(duration_s) AS min_dur,
  avg(duration_s) AS avg_dur,
  max(duration_s) AS max_dur
FROM data_analysis.cluster_stops
WHERE cid IS NOT NULL -- exclude outliers
GROUP BY cid; -- group all the stops centroids within the same cluster



CREATE INDEX idx_cluster_stops_mmsi_tbegin ON data_analysis.cluster_stops USING btree (mmsi,t begin);

CREATE TABLE data_analysis.tracks AS SELECT q1.mmsi, -- ship id
q1.cid as start_cid , -- start cluster node id of the track
q3.cid as end_cid , -- end cluster node id of the track
q1.t_end as t_start , -- track start is end of the previous stop 
q3.t_begin as t_end , -- track end is begin of the next stop 
extract(epoch FROM (q3.t_begin-q1.t_end))
as duration_s -- track duration in seconds
FROM (
SELECT mmsi, cid, tend
FROM data_analysis.cluster_stops WHERE cid IS NOT NULL ) as q1 INNER JOIN LATERAL (
-- track that are in between two clustered stops area
SELECT q2.cid, q2.t_begin
FROM data_analysis.cluster_stops as q2
WHERE q2.cid IS NOT NULL -- stop must be in a clustered area 
AND q1.mmsi=q2.mmsi -- same ship
AND q2.t_begin>q1.t_end -- search for the next stop event 
ORDER BY q2.t_begin LIMIT 1 ) as q3 ON (true);


-- create table for track geometry russian ships
ALTER TABLE data_analysis.susp_ship
ADD COLUMN track geometry(LineString ,4326) ;

UPDATE data_analysis.susp_ship
SET track = (
  SELECT ST_MakeLine(geom)
  FROM (
    SELECT geom
    FROM data_analysis.susp_ship
    WHERE mmsi = data_analysis.susp_ship.mmsi
    ORDER BY t
  ) subquery
)


-- add column for track geometry based on the positions from clustered stops
ALTER TABLE data_analysis.tracks
ADD COLUMN track geometry(LineString ,4230) ;

UPDATE data_analysis.tracks SET track = ( SELECT st_makeline (geom4230)
FROM (
SELECT geom4230
FROM ais_data.dynamic_ships
WHERE mmsi=tracks.mmsi AND t>=tracks.t_start AND t<=tracks.t_end ORDER BY t) as q1); -- order points by time


--Create table with edges between stop clusters
CREATE TABLE data_analysis.graph_edges 
AS SELECT
  start_cid , -- from node
  end_cid , -- to node
  nb_tracks , -- number of tracks
  q1.nb_ships , -- number of different ships
  q1.avg_duration , -- average transit time
  q1.avg_length , -- average transit length
  q1.min_length , -- minimum transit length
  st_makeline(c1.centroid ,c2.centroid) as straight_edge -- edge
FROM ( SELECT
  start_cid , -- from node
  end_cid , -- to node
  count(*) as nb_tracks , -- number of vessel trajectories
  count ( distinct mmsi) as nb_ships , -- number of unique ships
  avg(duration_s) as avg_duration , -- average trajectory duration
  avg(st_length(track)) as avg_length , -- average length
  min(st_length(track)) as min_length -- shortest length
FROM data_analysis.tracks
GROUP BY start_cid , end_cid ) as q1
LEFT JOIN data_analysis.clusters_stops_hulls as c1
ON (c1.cid=q1.start_cid)
LEFT JOIN data_analysis.clusters_stops_hulls as c2
ON (c2.cid=q1.end_cid);

--Create table with vessels wihin 100 meters from pipeline for more than 1 minute
CREATE TABLE data_analysis.vessels_pipeline AS 
SELECT pipname, mmsi, shipname, MIN(t) as min_t, MAX(t) as max_t, (MAX(t) - MIN(t)) as dur, geom3035
FROM context_data.pipeline as q1
INNER JOIN ais_data.dynamic_ships as q2
ON (
    speed>0
    t>='2023-02-12 07:00:00'
    AND t<'2023-02-12 12:00:00'
    AND ST_DWithin(q2.geomg3035,q1.geom,100)
    )
LEFT JOIN ais_data.static_ships as q4 
ON (q2.mmsi=q4.sourcemmsi)
GROUP BY pipname, mmsi, shipname, geom3035
HAVING (MAX(t) - MIN(t)) > INTERVAL '1 minute';


--Query to find the closest point on a line to a point
SELECT
  ST_Azimuth(ship_geom, line_segment) AS azimuth_angle, 
  ST_AsText(ship_geom) AS ship_position, 
  ST_AsText(line_segment) AS line_segment 
FROM 
  ais_data 
  JOIN line_data ON ST_Intersects(ship_geom, ST_Segmentize(line_geom, 0.01)) 
WHERE 
  ST_Distance(ship_geom, line_geom) < 0.1 
  AND ABS(ST_Azimuth(ship_geom, line_geom) - line_direction) < 5;

--Query to find the closest point on a line to a point
SELECT ST_Distance(dynamic_ships.geom4230, pipeline.geom) AS distance, mmsi
FROM ais_data.dynamic_ships
JOIN context_data.pipeline ON ST_DWithin(dynamic_ships.geom4230::geography, pipeline.geom::geography, 100)
WHERE 
  t>='2023-02-10 00:00:00'
  AND t<'2023-02-11 00:00:00'
GROUP BY distance, MMSI;

--create line geometry from the points
CREATE TABLE data_analysis.tracks_lines AS
SELECT mmsi,speed,id, ST_MakeLine(geom4230 ORDER BY timestamp) AS line
FROM ais_data.dynamic_ships
GROUP BY id, mmsi, speed;



-- CREATE table suspicious vessels
CREATE TABLE context_data.suspicious_vessels (
  mmsi integer,
  shipname text,
id bigserial,
  CONSTRAINT suspicious_vessels_pkey PRIMARY KEY (id)
);


-- CREATE table Join suspicious vessels with dynamic ships using the mmsi
CREATE table data_analysis.susp_ship as
SELECT *
FROM ais_data.dynamic_ships
JOIN context_data.suspicious_vessels ON dynamic_ships.mmsi = suspicious_vessels.sus_mmsi

-- Select vessels within 100 meters from pipeline for more than 30 minute and 100 points
SELECT 
  q1.mmsi, 
  COUNT(*) AS count_within_100m,
  EXTRACT(epoch FROM (MAX(t) - MIN(t))) AS time_diff
FROM 
  ais_data.dynamic_ships as q1
  JOIN context_data.pipeline as q2
    ON (ST_Distance(q1.geom3035, q2.geom) <= 100
	AND t>='2023-01-09 07:00:00'
    AND t<'2023-03-03 12:00:00')
	AND speed>0
GROUP BY 
  q1.mmsi
HAVING 
  COUNT(*) >= 100 AND
  EXTRACT(epoch FROM (MAX(t) - MIN(t))) >= 1800




--DK AIS

CREATE TABLE dk_ais.mobile_ships (
    timestamp text,
    mobile_type VARCHAR(50) NULL,
    mmsi INT,
    lat DECIMAL(9,6),
    lon DECIMAL(9,6),
    status_text VARCHAR(100) NULL,
    speed DECIMAL(5,2) NULL,
    heading INT NULL,
 	id bigserial,
  CONSTRAINT dk_dynamic_pkey PRIMARY KEY (id)
);

-- make data temporal
ALTER TABLE dk_ais.mobile_ships ADD COLUMN t timestamp without time zone;
UPDATE dk_ais.mobile_ships SET t = to_timestamp(timestamp,'DD/MM/YYYY HH24:MI:SS');

--make data geographic
-- create index on the time column
CREATE INDEX idx_dynamic_ships_time
ON dk_ais.mobile_ships 
USING btree (t) ; 

--make data geograpic
ALTER TABLE dk_ais.mobile_ships ADD COLUMN geom geometry(Point,4326);
UPDATE dk_ais.mobile_ships
SET geom=ST_SetSRID (ST_MakePoint(lon,lat),4326);

