#!/bin/bash

for file in /Users/luggerud/Desktop/Stordata_AIS/Datasett/Endelig_datasett/ais-status/*.csv
do
  psql -U postgres -w -d ING3209_AIS -c "\copy ais_data.static_ships(callsign,datetime,destination,eta,imo,mmsi,shipname,shiptype,shiptype_text,type) FROM '$file' DELIMITER ',' CSV HEADER;"
done
