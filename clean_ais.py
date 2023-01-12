#Directly from ChatGPT, not verified yet!

import pandas as pd

ais_data = pd.read_csv("path/to/ais_data.csv")

# remove rows with invalid latitude or longitude values
ais_data = ais_data[(ais_data["latitude"] > -90) & (ais_data["latitude"] < 90) &
                   (ais_data["longitude"] > -180) & (ais_data["longitude"] < 180)]

# remove rows with invalid speed values
ais_data = ais_data[ais_data["speed"] >= 0]

# remove rows with invalid course values
ais_data = ais_data[(ais_data["course"] >= 0) & (ais_data["course"] <= 359)]

# save the cleaned data to a new csv
ais_data.to_csv("path/to/cleaned_ais_data.csv", index=False)
