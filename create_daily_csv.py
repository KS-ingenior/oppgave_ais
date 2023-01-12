import os
import pandas as pd
from datetime import datetime

folder_path = "path/to/folder"

# get all csv files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# create a dictionary to store dataframes with keys as date
df_dict = {}

# iterate through csv files
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)

    # extract date from timestamp and use it as key
    date_str = datetime.strptime(df['timestamp'][0], '%Y-%m-%d %H:%M:%S.%f').date()
    day_str = date_str.strftime('%Y-%m-%d')
    if day_str in df_dict:
        df_dict[day_str] = pd.concat([df_dict[day_str], df])
    else:
        df_dict[day_str] = df

# concatenate dataframes for each date and save as csv
for day, df in df_dict.items():
    df.to_csv(f"{day}.csv", index=False)
