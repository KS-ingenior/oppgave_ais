# pip install psycopg2-binary pandas

import pandas as pd
from sqlalchemy import create_engine
import glob

# Database connection parameters
db_config = {
    'dbname': 'ING3209_AIS',
    'user': 'postgres',
    'password': 'your_password',  # Replace 'your_password' with your actual PostgreSQL password
    'host': 'localhost'
}

# SQLAlchemy engine for PostgreSQL
engine_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['dbname']}"
engine = create_engine(engine_url)

# Paths to the CSV files for static and dynamic ships
static_ships_path = '/Users/luggerud/Desktop/Stordata_AIS/Datasett/Endelig_datasett/ais-status/*.csv'
dynamic_ships_path = '/Users/luggerud/Desktop/Stordata_AIS/Datasett/Endelig_datasett/ais-pos/*.csv'

# Function to import CSV files into a PostgreSQL table
def import_csv_to_db(path, table_name, schema_name):
    csv_files = glob.glob(path)
    for file in csv_files:
        df = pd.read_csv(file)
        df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema_name)
        print(f"Imported {file} into {schema_name}.{table_name}")

# Import static ships
import_csv_to_db(static_ships_path, 'static_ships', 'ais_data')

# Import dynamic ships
import_csv_to_db(dynamic_ships_path, 'dynamic_ships', 'ais_data')

print("All files have been imported successfully.")
