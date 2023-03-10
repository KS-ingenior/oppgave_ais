import os
import pandas as pd
import numpy as np

folder_path = '/set/folder/path'

# iterate through all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        input_file = os.path.join(folder_path, file_name)
        output_file = os.path.join(folder_path, file_name[:-4] + '_CLEAN.csv')

        # read the input CSV file
        ais_data = pd.read_csv(input_file)

        # remove rows with invalid latitude or longitude values
        ais_data = ais_data[(ais_data["lat"] > -90) & (ais_data["lat"] < 90) &
                            (ais_data["lon"] > -180) & (ais_data["lon"] < 180)]

        # convert "speed" column to numeric type and set NaN values to NULL
        ais_data["speed"] = pd.to_numeric(ais_data["speed"], errors='coerce')
        ais_data["speed"] = ais_data["speed"].fillna(value=np.nan)

        # remove rows with invalid speed values
        ais_data = ais_data[(ais_data["speed"] >= 0) & (ais_data["speed"] <= 80)]

        # remove rows with invalid course values
        ais_data = ais_data[(ais_data["course"] >= 0) & (ais_data["course"] <= 359)]

        # save the cleaned data to a new CSV file
        ais_data.to_csv(output_file, index=False)

        print(f"Cleaned data saved to {output_file}")
