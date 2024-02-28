# pip install psycopg2-binary pandas

import pandas as pd
from sqlalchemy import create_engine
import glob

# Database connection parameters
db_config = {
    'dbname': 'ING3209',
    'user': 'postgres',
    'password': '1750',  # Replace 'your_password' with your actual PostgreSQL password
    'host': 'localhost',
    'port': '1234'  # Specify the port number here
}

# SQLAlchemy engine for PostgreSQL
engine_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
engine = create_engine(engine_url)

# Paths to the CSV files for static and dynamic ships
#static_ships_path = r'C:\Users\MilGeo2\Documents\Stordata (AIS) 2024\AIS-data pr dag\ais-status/*.csv'
dynamic_ships_path = r'C:\Users\MilGeo2\Documents\Stordata (AIS) 2024\AIS-data pr dag\ais-pos/*.csv'  # Provide the correct path here

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
    'mmsi': 'mmsi',
    'type': 'type',
    'imo': 'imo',
    'callsign': 'callsign',
    'shipname': 'shipname',
    'shiptype': 'shiptype',
    'shiptype_text': 'shiptype_text',
    'eta': 'eta',
    'destination': 'destination',
    'timestamp_utc': 'timestamp_utc',
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
#import_csv_to_db(static_ships_path, 'static_ships', 'ais_data', static_ships_column_mapping)

# Import dynamic ships with column mapping
import_csv_to_db(dynamic_ships_path, 'dynamic_ships', 'ais_data', dynamic_ships_column_mapping)

print("All files have been imported successfully.")
