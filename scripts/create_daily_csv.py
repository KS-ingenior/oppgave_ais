import os
import pandas as pd

# specify the directory containing the CSV files
dir = '../ais-new/ais-pos'
#dir = '../ais-new/ais-status'

# get a list of all CSV files in the directory
csv_files = [f for f in os.listdir(dir) if f.endswith('.csv')]

# create an empty list to store the dataframe
df_list = []

# loop through the CSV files and join the values
for file in csv_files:
    temp_df = pd.read_csv(os.path.join(dir, file))
    df_list.append(temp_df)

# join all dataframe using concat
df = pd.concat(df_list)

# Define the directory for storing all daily CSV files
daily_csv_dir = os.path.join(dir, "daily_csv_files")
if not os.path.exists(daily_csv_dir):
    os.makedirs(daily_csv_dir)

# group the data by date and write new CSV files
for date, group in df.groupby(df['timestamp_utc'].str[:10]):
    # Define the file path for the new CSV file within the daily CSV directory
    new_file_path = os.path.join(daily_csv_dir, f'{date}.csv')
    group.to_csv(new_file_path, index=False)
