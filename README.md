# Bakgrunn
Dette repoet inneholder info om oppgaven og datasettet som bruker i stordata-uka på milgeofordypningen på KSING. Det inneholder både link til datasettet, informasjon om datasettet, samt noen verktøy som kan hjelpe deg med å bearbeide dataene før de imporeteres inn i PostgresSQL-databasen.

# Hensikt
Oppgaven skal hjelpe dere med..., samt bli kjent med QGIS

# Programvare
* [PostgreSQL med PostGIS extension](https://www.postgresql.org/download/)
* [QGIS](https://qgis.org/en/site/forusers/download.html)

# Datasett
Kan lastes ned [her](https://drive.google.com/file/d/1C5RwRdRgCSQ0EP-kysDz_dI5AcpxKXXP/view?usp=share_link). Datasettet er lastet ned fra Kystverkets åpne datastrøm. Denne datastrømmen har noen begrensninger:
- Gjelder for det geografiske område innenfor norsk økonomisk sone, fiskerivernsonen ved Svalbard og vernesonen ved Jan Mayen.
- Viser ikke fiskefartøy under 15 meter.
- Viser ikke fritidsfartøy under 45 meter.

## Kilder
* Kystverket


## Datakvalitet
**MÅ OPPDATERES**

Datasettet er ikke kontinuerlig, men har tre tidsperioder som er mer eller mindre komplette.
- 9 jan - 18 jan 23
- 10 feb -  16 feb 23
- 22 feb - 08 mar 23

I tillegg er det noen timer opprom innen i de ulike periodene som ikke har data.

Totalt 32 døgn med data
![Bilde av dekningsområdet](https://developer.barentswatch.no/assets/images/OpenAisArea2-c5332d2a6ed8f25fba1b5b064ad72b38.PNG)

# Lure triks 
I mappen [scripts](scripts) ligger det noen nyttige scripts som kan hjelpe dere med å importere data og rense dataene deres.

# SQL

## PostGRESQL
PostgreSQL, often referred to simply as Postgres, is a powerful, open-source object-relational database management system (ORDBMS). It has earned a strong reputation for its proven architecture, reliability, data integrity, robust feature set, and extensibility. Here's a quick introduction to some of its key features and aspects:

### Key Features

1. **SQL Compliance**: PostgreSQL is highly compliant with the SQL standard and supports a wide range of SQL data types, including primitive types (integer, numeric, string, boolean), structured types (date/time, array, range), document types (JSON, XML, hstore), and geometry types (point, line, lseg, polygon, etc.).

2. **ACID Compliance**: Ensures database transactions are processed reliably through its support for Atomicity, Consistency, Isolation, and Durability (ACID).

3. **Extensibility**: Users can extend PostgreSQL using its support for stored procedures and functions, custom data types, and custom indexes. It also supports various programming languages for writing stored procedures, such as PL/pgSQL (its native language), PL/Python, PL/Perl, and others.

4. **Concurrency and Performance**: Implements Multi-Version Concurrency Control (MVCC) to ensure system performance and allow for concurrent transactions without locking reads, enhancing both performance and scalability.

5. **Advanced Indexing**: Supports multiple types of indexing, including B-tree, Hash, GiST, SP-GiST, GIN, and BRIN, allowing for faster data retrieval and efficient query execution.

6. **Replication and High Availability**: Offers several built-in replication features, such as streaming replication and logical replication, to ensure data durability and high availability.

7. **Security**: Provides robust security features, including strong access-control mechanisms, SSL support for data encryption, and row-level security.

8. **Full Text Search**: Includes powerful full-text search capabilities that can search through large datasets to find matching strings, words, or phrases.

9. **Internationalization**: Supports international character sets, including multibyte character encodings and full support for Unicode.

   Kilde: CHATGPT

### Use Cases

PostgreSQL is used for a wide range of applications, from simple websites to complex web services, financial systems, geographic information systems (GIS), and much more. Its versatility, reliability, and open-source nature make it a favored choice among developers, businesses, and government organizations.


## POSTGIS
PostGIS (/ˈpoʊstdʒɪs/ POST-jis) is an open source software program that adds support for geographic objects to the PostgreSQL object-relational database. PostGIS follows the Simple Features for SQL specification from the Open Geospatial Consortium (OGC). (https://en.wikipedia.org/wiki/PostGIS) 

PostGIS is an open-source extension for the PostgreSQL database that adds support for geographic objects, allowing it to be used as a spatial database for geographic information systems (GIS), much like an extension of the SQL standard for spatial data. This extension enables PostgreSQL to store, query, and manipulate spatial data, facilitating the analysis of geographic information and the management of location-based data.

Key Features of PostGIS
1. Spatial Data Types: PostGIS introduces spatial data types such as GEOMETRY and GEOGRAPHY, which can represent points, lines, polygons, and other geometric shapes in two and three dimensions.

2. Spatial Functions: It provides a wide range of functions for performing operations on spatial data, including spatial relationships and measurements (e.g., distance, area, intersection, and containment), geometry processing (e.g., simplification, validation, and transformation), and spatial indexing for efficient querying.

3. Spatial Indexing: Uses R-tree-based indexing through GiST (Generalized Search Tree) to efficiently query and manipulate large spatial data sets.

4. Support for Raster Data: Besides geometric data, PostGIS also supports raster data, enabling the storage, analysis, and processing of pixelated data sets such as satellite imagery and digital elevation models.

5. Integration with GIS Software: PostGIS is widely supported by many GIS software packages, both open-source (e.g., QGIS, GRASS GIS) and proprietary (e.g., ESRI ArcGIS), allowing for easy integration of spatial data managed in PostgreSQL with various GIS applications.

6. Standards Compliant: It adheres to the Open Geospatial Consortium (OGC) standards, including the Simple Features for SQL specification, ensuring compatibility with other GIS solutions and promoting interoperability.

## POSTGIS and QGIS



[^1]: https://www.barentswatch.no/artikler/tilbyr-apne-ais-data/
