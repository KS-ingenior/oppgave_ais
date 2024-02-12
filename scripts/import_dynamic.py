import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import glob

# PostgreSQL connection parameters
db_config = {
    'dbname': 'ING3209_AIS',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost'
}

# Path to the CSV files
path = '/Users/luggerud/Desktop/Stordata_AIS/Datasett/Endelig_datasett/ais-pos/*.csv'

# SQLAlchemy engine for PostgreSQL
# Adjust the URL based on your PostgreSQL credentials and database
engine_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['dbname']}"
engine = create_engine(engine_url)

# Find all CSV files in the specified directory
csv_files = glob.glob(path)

# Loop through each CSV file, load it into a pandas DataFrame, and insert into the database
for file in csv_files:
    df = pd.read_csv(file)
    # Insert the DataFrame into the database; adjust the 'name' parameter to your target table name
    # If the table does not exist, it will be created; if it does, data will be appended
    df.to_sql('dynamic_ships', engine, if_exists='append', index=False, schema='ais_data')
    print(f"Imported {file}")

print("All files have been imported successfully.")
