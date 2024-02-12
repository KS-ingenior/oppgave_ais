# Scripts

I denne mappen ligger følgende:

## clean_ais
AIS-data har endel støy/feil i seg og må "renses" før de importeres inn i en SQL-database

## import_AIS_postgres.py
This script will handle CSV files from two different directories—one for static ships and another for dynamic ships—and import them into their respective tables in the database.

Defines a function import_csv_to_db that takes the path to the CSV files, the target table name, and the schema name. It reads each CSV file into a pandas DataFrame and imports the data into the specified table in the PostgreSQL database.

Calls this function twice, once for each set of CSV files (static and dynamic ships), specifying the appropriate table names (static_ships and dynamic_ships) and the schema name (ais_data).

Remember to replace 'your_password' with your actual PostgreSQL password and adjust the database connection parameters as needed. Also, ensure the table names and schema names match those in your database, and that the column names in your CSV files align with those in your database tables.

In the context of using pandas with SQLAlchemy for importing CSV files into a PostgreSQL database, specifying the schema is necessary only if the target tables are not in the default schema (which is usually public in PostgreSQL). If your tables are located in a different schema, you must specify the schema name to ensure that the data is inserted into the correct tables. This is common in databases that use multiple schemas to organize tables logically.

In the script I provided, the schema parameter in the df.to_sql method is used to specify the schema name:

`df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema_name)`

Here, schema_name should be replaced with the name of the schema where your tables (static_ships and dynamic_ships) are located. For example, if you're using a schema named ais_data, you should provide it as the schema_name argument when calling import_csv_to_db.

If your tables are in the PostgreSQL default public schema, you could omit the schema parameter or set it to 'public'. However, in the script, since the schema name is explicitly mentioned (ais_data), it implies that the tables are expected to be within that specific schema.

If you're unsure about the schema where your tables reside, you can check your database schema setup or consult with your database administrator. In most cases, if you have created custom schemas for organizing your database objects, you should provide the schema name in your script as shown. This approach helps in maintaining clarity and ensures that the data is inserted into the correct place, especially in more complex databases with multiple schemas.

## import
