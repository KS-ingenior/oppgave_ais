#!/bin/bash

for file in /Users/luggerud/Desktop/Stordata_AIS/Datasett/Endelig_datasett/ais-pos/*.csv
do
  psql -U postgres -w -d ING3209_AIS -c "\copy ais_data.dynamic_ships(course, datetime, heading, lat, lon, mmsi, speed, status_text, turn, type) FROM '$file' DELIMITER ',' CSV HEADER;"
done
