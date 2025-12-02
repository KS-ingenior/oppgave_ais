#remember to check if you have installed the right Python packages. If not use pip install pandas.
#Double check that the column mapping is correct and fits your database

import pandas as pd
from sqlalchemy import create_engine
import glob

# Database connection parameters
db_config = {
    'dbname': 'INGOF3205',#change if needed
    'user': 'postgres',#change if needed
    'password': '',#change if needed
    'host': 'localhost',#change if needed
    'port': '5432', #change if needed
}

# SQLAlchemy engine for PostgreSQL
engine_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
engine = create_engine(engine_url)

# Paths to the CSV files for static and dynamic ships (change to your actual file path)
static_ships_path = 'C:/insert/correct/filepath/ais-status/*.csv' # Provide the correct path here and hash/unhash depending on your import
#dynamic_ships_path = 'C:/insert/correct/filepath/ais-pos/*.csv'  # Provide the correct path here and hash/unhash depending on your impor

# Function to import CSV files into a PostgreSQL table
def import_csv_to_db(path, table_name, schema_name, column_mapping=None):
    csv_files = glob.glob(path)
    for file in csv_files:
        df = pd.read_csv(file)
        if column_mapping:
            df = df.rename(columns=column_mapping)
        df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema_name)
        print(f"Imported {file} into {schema_name}.{table_name}")

# Define column mapping for static ships
static_ships_column_mapping = {
    'mmsi': 'sourcemmsi',
    'type': 'type',
    'imo': 'imo',
    'callsign': 'callsign',
    'shipname': 'shipname',
    'shiptype': 'shiptype',
    'shiptype_text': 'shiptype_text',
    'eta': 'eta',
    'destination': 'destination',
    'timestamp_utc': 'datetime',
}

# Define column mapping for dynamic ships
dynamic_ships_column_mapping = {
     'mmsi': 'mmsi',
     'type': 'type',
     'lat': 'lat',
     'lon': 'lon',
     'course': 'course',
     'heading': 'heading',
     'speed': 'speed',
     'turn': 'turn',
     'status_text': 'status_text',
     'timestamp_utc': 'datetime',
 }

# Import static ships with column mapping
import_csv_to_db(static_ships_path, 'static_ships', 'ais_data', static_ships_column_mapping)

# Import dynamic ships with column mapping
#import_csv_to_db(dynamic_ships_path, 'dynamic_ships', 'ais_data', dynamic_ships_column_mapping)

print("All files have been imported successfully.")
