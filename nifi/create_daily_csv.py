import os
import pandas as pd
from datetime import datetime

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

# convert timestamp column to datetime format
df['datetime'] = pd.to_datetime(df['timestamp_utc'], format='%Y-%m-%d %H:%M:%S.%f')

#sort the dataframe by datetime
df.sort_values(by='datetime', inplace=True)

# group the data by date and write new CSV files
for date, group in df.groupby(df['datetime'].dt.date):
    new_file = f'{date}.csv'
    group.to_csv(os.path.join(dir, new_file), index=False)
