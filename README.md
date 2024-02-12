# Bakgrunn
Dette repoet inneholder info om oppgaven og datasettet som bruker i stordata-uka på milgeofordypningen på KSING. Det inneholder både link til datasettet, informasjon om datasettet, samt noen verktøy som kan hjelpe deg med å bearbeide dataene før de imporeteres inn i PostgresSQL-databasen.

# Hensikt
Oppgaven skal hjelpe dere med..., samt bli kjent med QGIS

# Programvare
* [PostgreSQL med PostGIS extension](https://www.postgresql.org/download/)
* [QGIS](https://qgis.org/en/site/forusers/download.html)

# Datasett
Kan lastes ned [her](https://drive.google.com/file/d/1C5RwRdRgCSQ0EP-kysDz_dI5AcpxKXXP/view?usp=share_link). Datasettet er lastet ned fra Kystverkets åpne datastrøm. Denne datastrømmen har noen begrensninger:
- Gjelder for det geografiske område innenfor norsk økonomisk sone, fiskerivernsonen ved Svalbard og vernesonen ved Jan Mayen.
- Viser ikke fiskefartøy under 15 meter.
- Viser ikke fritidsfartøy under 45 meter.

![Bilde av dekningsområdet](https://developer.barentswatch.no/assets/images/OpenAisArea2-c5332d2a6ed8f25fba1b5b064ad72b38.PNG)

# Lure triks 
I mappen [scripts](scripts) ligger det noen nyttige scripts som kan hjelpe dere med å importere data og rense dataene deres.

# Kilder
* Kystverket


## Datakvalitet
**MÅ OPPDATERES**

Datasettet er ikke kontinuerlig, men har tre tidsperioder som er mer eller mindre komplette.
- 9 jan - 18 jan 23
- 10 feb -  16 feb 23
- 22 feb - 08 mar 23

I tillegg er det noen timer opprom innen i de ulike periodene som ikke har data.

Totalt 32 døgn med data



[^1]: https://www.barentswatch.no/artikler/tilbyr-apne-ais-data/
