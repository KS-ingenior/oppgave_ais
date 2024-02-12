# Nedlasting av AIS-data

Flow: ![NIFI Flow](nifi/NIFI-Flow-AIS.JPG)

NiFi template: [Template i XML](nifi/AIS-lagre-som-CSV-final.xml)

Nifi tilgjengelig her: http://ksing.duckdns.org:8443/nifi/






### Maskinvare
Virtuell maskin etablert i [Google Cloud](https://cloud.google.com/). 

| Machine config  |  |
| ------------- | ------------- |
| Machine type | e2-medium |
| CPU platform | Intel Broadwell  |
| Architecture | x86/64 |
| OS | Ubuntu 20.04 |
| Nifi version | 16.3 |


## Slå sammen til en CSV pr dag
Kjør [dette](create_daily_csv.py) skriptet for å slå sammen og lage en CSV-fil pr døgn. Skriptet leser igjennom alle CSV-filene i mappen (evt endre folder path), sorterer basert på kolonnen 'timestamp_utc' og lagrer nye CSV-filer etter formatet YYYY-MM-DD.
