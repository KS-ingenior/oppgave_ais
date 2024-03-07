# Background
This repository contains information about the task and dataset used. It includes links to the dataset, information about the dataset, as well as some tools that can help you process the data before importing it into the PostgreSQL database.

## Purpose
The task aims to help you work with large unwieldy datasets and to familiarize you with QGIS as a tool.


## Software
The following software needs to be downloaded and installed:
* [PostgreSQL med PostGIS extension](https://www.postgresql.org/download/)
* [QGIS](https://qgis.org/en/site/forusers/download.html)
* [Python](https://www.python.org/)
 



# Dataset
Can be downloaded [here](https://drive.google.com/file/d/1jICGKZWZsahZKWO_HfnoSPi9EUVjixmO/view?usp=sharing). The dataset is downloaded from the [Norwegian Coastal Administration's open data stream.](https://www.kystverket.no/navigasjonstjenester/ais/tilgang-pa-ais-data/)

## Limitations
This data stream has some limitations:

* Applies to the geographical area within the Norwegian economic zone, the fisheries protection zone around Svalbard, and the protection zone around Jan Mayen.
* Does not show fishing vessels under 15 meters.
* Does not show recreational vessels under 45 meters.

## Timeframe
* 22 February 2023 - 28 March 2023


## Coverage of Norwegian AIS data
![Bilde av dekningsområdet](https://developer.barentswatch.no/assets/images/OpenAisArea2-c5332d2a6ed8f25fba1b5b064ad72b38.PNG)

## Additional data
If needed, it is possible to [download](https://web.ais.dk/aisdata/) additional data from [Danish Maritime Authority](https://dma.dk/safety-at-sea/navigational-information/ais-data). Aprrox coverage for these data is as shown below: ![image](https://github.com/KS-ingenior/oppgave_ais_data/assets/156073833/672de51c-32ff-4663-b96d-6e234b762017)



# Tutorials
1. A basic introduction to SQL is provided here: (https://www.postgresql.org/docs/15/tutorial.html)
2. A basic POSTGIS tutorial is found here: (https://postgis.net/workshops/postgis-intro/index.html)
3. A more specific and specialized tutorial utilizing the POSTGIS functionality on AIS data in a maritime environment is provided here: (https://hal.science/hal-03137050v1)

# Useful scripts
In the folder [scripts](scripts) there are several useful scripts that will help you with preparing and cleaning your data prior to importing them in to your database.

# SQL
Structured query language (SQL) is a programming language for storing and processing information in a relational database. A relational database stores information in tabular form, with rows and columns representing different data attributes and the various relationships between the data values. You can use SQL statements to store, update, remove, search, and retrieve information from the database. You can also use SQL to maintain and optimize database performance.

Structured query language (SQL) is a popular query language that is frequently used in all types of applications. Data analysts and developers learn and use SQL because it integrates well with different programming languages. For example, they can embed SQL queries with the Java programming language to build high-performing data processing applications with major SQL database systems such as Oracle or MS SQL Server. SQL is also fairly easy to learn as it uses common English keywords in its statements.

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


## POSTGIS
PostGIS (/ˈpoʊstdʒɪs/ POST-jis) is an open source software program that adds support for geographic objects to the PostgreSQL object-relational database. PostGIS follows the Simple Features for SQL specification from the Open Geospatial Consortium (OGC). (https://en.wikipedia.org/wiki/PostGIS) 

PostGIS is an open-source extension for the PostgreSQL database that adds support for geographic objects, allowing it to be used as a spatial database for geographic information systems (GIS), much like an extension of the SQL standard for spatial data. This extension enables PostgreSQL to store, query, and manipulate spatial data, facilitating the analysis of geographic information and the management of location-based data.

**Key Features of PostGIS**
1. Spatial Data Types: PostGIS introduces spatial data types such as GEOMETRY and GEOGRAPHY, which can represent points, lines, polygons, and other geometric shapes in two and three dimensions.

2. Spatial Functions: It provides a wide range of functions for performing operations on spatial data, including spatial relationships and measurements (e.g., distance, area, intersection, and containment), geometry processing (e.g., simplification, validation, and transformation), and spatial indexing for efficient querying.

3. Spatial Indexing: Uses R-tree-based indexing through GiST (Generalized Search Tree) to efficiently query and manipulate large spatial data sets.

4. Support for Raster Data: Besides geometric data, PostGIS also supports raster data, enabling the storage, analysis, and processing of pixelated data sets such as satellite imagery and digital elevation models.

5. Integration with GIS Software: PostGIS is widely supported by many GIS software packages, both open-source (e.g., QGIS, GRASS GIS) and proprietary (e.g., ESRI ArcGIS), allowing for easy integration of spatial data managed in PostgreSQL with various GIS applications.

6. Standards Compliant: It adheres to the Open Geospatial Consortium (OGC) standards, including the Simple Features for SQL specification, ensuring compatibility with other GIS solutions and promoting interoperability.

## POSTGIS and QGIS
The relationship between PostGIS and QGIS is one of powerful integration, where PostGIS serves as the spatial database backend and QGIS as the front-end geographic information system (GIS) software. This combination allows users to manage, analyze, and visualize spatial data effectively. Here's an overview of how PostGIS and QGIS work together and the benefits of their integration:

PostGIS: The Spatial Database
PostGIS extends PostgreSQL with support for geographic objects, enabling the database to store, query, and manipulate spatial data. It is designed to handle a wide range of spatial data types and operations, making it an ideal choice for storing large volumes of geospatial data.

QGIS: The GIS Front-end
QGIS is an open-source GIS application that provides tools for data editing, viewing, analysis, and composition. It supports various vector, raster, and database formats, including direct integration with PostGIS. QGIS allows users to create sophisticated maps, perform spatial analysis, and manage geographic data.

1. Integration Benefits
Seamless Data Management: QGIS users can connect directly to a PostGIS database, enabling them to view, edit, and manage spatial data stored in PostGIS without the need for data conversion or import/export processes. This direct connection simplifies workflows and ensures that data remains centralized and up-to-date.

2. Advanced Spatial Analysis: Combining QGIS's analytical tools with PostGIS's spatial functions allows for complex spatial analyses. Users can execute spatial queries and analyses directly on the database and visualize the results in QGIS, leveraging the strengths of both systems.

3. Collaborative and Multi-User Environment: With data stored in a PostGIS database, multiple QGIS users can access and work on the same datasets concurrently. This setup supports collaborative projects and ensures data consistency across an organization.

4. High Performance for Large Datasets: PostGIS is optimized for high performance with large spatial datasets. When used as a backend for QGIS, it allows for efficient querying and manipulation of large volumes of spatial data, making it suitable for enterprise-level GIS projects.

5. Open Standards and Interoperability: Both QGIS and PostGIS adhere to open standards, ensuring compatibility and interoperability with other GIS software and systems. This openness facilitates the exchange of data and integration with other tools and platforms.

### ArcGIS vs POSTGIS
Choosing between QGIS (with PostGIS) and ArcGIS (with PostGIS) for your spatial data management and GIS needs involves considering various factors such as cost, functionality, flexibility, community support, and licensing. Here’s a comparison to help you understand why you might choose QGIS and PostGIS over ArcGIS and PostGIS for your projects:

**Cost and Licensing**

- **QGIS**: QGIS is free and open-source, making it accessible to anyone without the need for purchasing licenses. This can significantly reduce costs for individuals, small businesses, and large organizations, especially when deploying on multiple workstations.
- **ArcGIS**: ArcGIS is a proprietary software developed by Esri, requiring paid licenses for use. While ArcGIS offers a comprehensive suite of tools and is widely used in industry and academia, the cost can be a barrier for some users or projects.

**Open Source and Community Support**

- **QGIS**: Being open-source, QGIS benefits from a large, active community that contributes plugins, tools, and documentation. Users have the flexibility to modify the software to meet their needs and can access a wealth of community-generated resources and support.
- **ArcGIS**: While ArcGIS has a strong user community and extensive documentation, the ability to customize or extend the software is limited compared to open-source alternatives. Users depend on Esri for updates, new features, and technical support.

**Interoperability and Standards**

- **QGIS and PostGIS**: Both are built with a commitment to open standards and interoperability, making it easier to integrate with other systems and share data across platforms. PostGIS enhances QGIS with powerful spatial database capabilities, allowing for efficient management and analysis of large datasets.
- **ArcGIS and PostGIS**: ArcGIS supports connections to PostGIS, but being a proprietary product, might have limitations or restrictions when integrating with other open-source tools or databases. However, Esri has made efforts to support industry standards and interoperability.

**Functionality and Usability**

- **QGIS**: Offers a wide range of GIS tools and functionalities through its core features and extensive plugin library. While QGIS is highly capable, some advanced or specialized tools might only be available through third-party plugins, which can vary in quality and documentation.
- **ArcGIS**: Known for its comprehensive suite of advanced GIS, spatial analysis, and mapping tools. ArcGIS is often considered more polished in terms of user interface and integrated workflows, which can be a deciding factor for organizations with complex GIS needs.

**Scalability and Performance**

- **Both QGIS and ArcGIS** can be effectively used with PostGIS for managing and analyzing spatial data. The choice might come down to the specific requirements of your project, such as the need for advanced analysis, the scale of data, or the availability of IT support and expertise.

The decision to use QGIS with PostGIS instead of ArcGIS with PostGIS often hinges on the need for a cost-effective, flexible, and community-supported GIS platform that is capable of handling professional-grade spatial analysis and data management. For organizations and individuals with limited budgets, a preference for open-source solutions, or the need for a highly customizable GIS environment, QGIS and PostGIS present a compelling option. However, for those who require specific advanced functionalities, seamless integration of various GIS tasks, or have established workflows in ArcGIS, the ArcGIS ecosystem may be worth the investment.

[^1]: https://www.barentswatch.no/artikler/tilbyr-apne-ais-data/
