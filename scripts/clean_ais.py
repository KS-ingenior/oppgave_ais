import os
import pandas as pd
import numpy as np

folder_path = r'set/folder/path' # set the correct folder path to where you have stored the data
output_folder = os.path.join(folder_path, 'Cleaned')

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)
print(f"Output folder '{output_folder}' is ready.")

# Iterate through all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        input_file = os.path.join(folder_path, file_name)
        output_file = os.path.join(output_folder, file_name[:-4] + '_CLEAN.csv')

        try:
            # Read the input CSV file
            ais_data = pd.read_csv(input_file)

            # Remove rows with invalid latitude or longitude values or values far outside Norway
            ais_data = ais_data[
                (ais_data["lat"] > 50) & (ais_data["lat"] < 90) &
                (ais_data["lon"] > -10) & (ais_data["lon"] < 45)
            ]

            # Convert "speed" column to numeric type and set NaN values to NULL
            ais_data["speed"] = pd.to_numeric(ais_data["speed"], errors='coerce')
            ais_data["speed"] = ais_data["speed"].fillna(value=np.nan)

            # Remove rows with invalid speed values
            ais_data = ais_data[(ais_data["speed"] >= 0) & (ais_data["speed"] <= 80)]

            # Remove rows with invalid course values
            ais_data = ais_data[(ais_data["course"] >= 0) & (ais_data["course"] <= 360)]

            # Save the cleaned data to a new CSV file
            ais_data.to_csv(output_file, index=False)
            print(f"Cleaned data saved to {output_file}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
