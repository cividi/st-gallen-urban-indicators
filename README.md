[![publish to dfour](https://github.com/cividi/st-gallen-urban-indicators/actions/workflows/sync.yaml/badge.svg)](https://github.com/cividi/st-gallen-urban-indicators/actions/workflows/sync.yaml)

# Urban Indicators St. Gallen

A work in progress repository collecting data, links to datasets and analysis for indicators on

Table of contents
1. [rental prices](#rental-prices)
2. [public space qualities](#streetwise)
2. [mobility](#mobility)
3. imissions like noise

compiling visual maps, automatically published to [dføur](https://dfour.space): [https://sandbox.dfour.space/de/0SF96/M3JDL6/](https://sandbox.dfour.space/de/0SF96/M3JDL6/)

## Data Package

All data in this repository is packaged as a [Frictionless](https://frictionlessdata.io) [Data Package](https://specs.frictionlessdata.io/data-package/). Some aspects are presented below in a human readable way. For details please check [datapackage.json](datapackage.json).

All maps presented in the [output workspace](https://sandbox.dfour.space/de/0SF96/M3JDL6/) are based on the [spatial data package](https://github.com/cividi/spatial-data-package), a building block for [dføur](https://dfour.space), a spatial data collaboration platform used above and available as open source as [spatial data package platform](https://github.com/cividi/spatial-data-package-platform).

## Rental Prices

### Method / Source

In broad strokes the collection and analysis of rent prices follows the following steps
1. Incremental (Crawler) collection of advertisements from public portals, e.g. Homegate into a PostgreSQL database and geocoding addresses with [Swisstopo REST Service](https://api3.geo.admin.ch/services/sdiservices.html#search)
2. Periodically (GitHub Action)
   - enriching the collected entries with official area, floor, building year from [housing data](https://www.housing-stat.ch) through heuristically matching housing portal entries to registered apartments
   - Calculating rent per room and per square meter
   - Group apartments by "size class" depending on number of rooms

Python frameworks and libraries used: [scrapy](https://docs.scrapy.org/en/latest/index.html), [frictionless-py](https://framework.frictionlessdata.io), [sqlalchemy](https://docs.sqlalchemy.org/en/14/)

### Data

*Note*: GWR data for the purpose of the St. Gallen Hack is available on request (find Viktoria or Thorben on the Discord).

#### Price Monitoring
- 📈 CSV: [data/price-monitoring/price-monitoring.csv](data/price-monitoring/price-monitoring.csv)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**CSV Schema**

| name           | type     | title                        | description                                                                        | format |
| -------------- | -------- | ---------------------------- | ---------------------------------------------------------------------------------- | ------ |
| id             | integer  | ID                           | The canonical homegate id                                                          |        |
| object_ref     | string   | Object Reference             | Reference (set by the advertiser)                                                  |        |
| category       | string   | Category                     | Category (set by the advertiser)                                                   |        |
| date           | datetime | Date and Time                | Date and time ad was first seen                                                    | any    |
| flatType       | any      | Flat Type                    | Flat type (set by the advertiser)                                                  |        |
| floor          | string   | Floor                        | Floor (set by the advertiser)                                                      |        |
| rent           | integer  | Rent                         | Monthly rent price including utility costs                                         |        |
| rent_add       | integer  | Monthly utility price        | Utility                                                                            |        |
| rent_net       | integer  | Net rent                     | Monthly rent price excluding utlility costs                                        |        |
| rooms          | any      | Number of rooms              | Number of rooms (set by the advertiser)                                            |        |
| area           | integer  | Apartment Surface            | Apartment surface in square meters (set by the advertiser)                         |        |
| year_built     | integer  | Construction year            | Year the building was constructed (set by the advertiser)                          |        |
| street_number  | string   | Street Name and House Number | Street name and house number of apartment (set by the advertiser)                  |        |
| city           | string   | City Name                    | City name of apartment (set by the advertiser)                                     |        |
| zip            | integer  | ZIP code                     | ZIP code of apartment (set by the advertiser)                                      |        |
| lat            | number   | Latitude                     | WGS84 (GPS) Latitude of building                                                   |        |
| lng            | number   | Longitude                    | WGS84 (GPS) Longitude of building                                                  |        |
| wkt            | string   | WKT Representation           | Well Known Text representation of latitude and longitude                           |        |
| gwr_egid       | integer  | GWR EGID                     | Matched federal building id from housing register (from address via Swisstopo/GWR) |        |
| match_accuracy | number   | Accuracy of GWR match        | Overlap of GWR entry and homegate data                                             |        |
| price_per_sqm  | number   | Price per sqm                | Price per square meter (square meters based on GWR match)                          |        |
| price_per_room | number   | Price per room               | Price per room (rooms based on GWR match)                                          |        |
| flat_cat       | string   | Size class                   | Size class of apartment (S, M or L)                                                |        |
| cat            | string   | Color class                  | Class for coloring                                                                 |        |

#### Price Monitoring extended

- 📈 CSV: [data/price-monitoring/price-monitoring-extended.csv](data/price-monitoring/price-monitoring-extended.csv)
- 🗺 Styled GeoJSON (S): [snapshots/geojson/homegate-styled-S.geojson](snapshots/geojson/homegate-styled-S.geojson)
- 🗺 Styled GeoJSON (M): [snapshots/geojson/homegate-styled-M.geojson](snapshots/geojson/homegate-styled-M.geojson)
- 🗺 Styled GeoJSON (L): [snapshots/geojson/homegate-styled-L.geojson](snapshots/geojson/homegate-styled-L.geojson)
- 📦 Snapshot (S): [snapshots/01-rent-prices-S.json](snapshots/01-rent-prices-S.json)
- 📦 Snapshot (M): [snapshots/01-rent-prices-M.json](snapshots/01-rent-prices-M.json)
- 📦 Snapshot (L): [snapshots/01-rent-prices-L.json](snapshots/01-rent-prices-L.json)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**CSV Schema**

⚠️ Note: only additional columns (compared to `data/price-monitoring/price-monitoring.csv`) are shown here, for additional columns see above.

| name           | type     | title                        | description                                                                        | format |
| -------------- | -------- | ---------------------------- | ---------------------------------------------------------------------------------- | ------ |
| egid                | integer  | GWR EGID                        | Matched federal building id from housing register (from address via Swisstopo/GWR)                           |        |
| ren_potential       | boolean  | Renovation potential            | Building did undergoe renovation since construction                                                          |        |
| LR_DAY              | number   | Immissionswert Lr Nacht [dB(A)] | Berechneter Immissionspegel in der Nacht je Gebäude (Berechnungsmethode: Hausbeurteilung)                    |        |
| LR_NIGHT            | number   | Immissionswert Lr Tag [dB(A)]   | Berechneter Immissionspegel am Tag je Gebäude (Berechnungsmethode: Hausbeurteilung)                          |        |
| ES                  | string   | Empfindlichkeitsstufe (ES)      | Empfindlichkeitsstufen aus dem Zonenplan Kanton St.Gallen (Datenmodell ID 145)                               |        |
| COMM_USE_D          | string   | Nutzung                         | Gebäudenutzungen aus dem eidg. Gebäude- und Wohnungsregister (GWR), https://www.housing-stat.ch/de/home.html |        |
| EXP_LIM_D           | string   | Lärmbeurteilung Tag             | Strassenlärmbeurteilung nach dem Belastungsgrenzwert am Tag gemäss der Lärmschutz-Verordnung                 |        |
| EXP_LIM_N           | string   | Lärmbeurteilung Nacht           | Strassenlärmbeurteilung nach dem Belastungsgrenzwert in der Nacht gemäss der Lärmschutz-Verordnung           |        |
| EXP_LIM             | string   | Lärmbeurteilung                 | Strassenlärmbeurteilung nach dem Belastungsgrenzwert (Tag und Nacht) gemäss der Lärmschutz-Verordnung        |        |
| noise_below         | boolean  | Immission values                | Lärmbeurteilung >IGW und/oder >AW / >PW                                                                      |        |
| quartier_nummer     | integer  | Quartier Nummer                 | Nummer Quartier                                                                                              |        |
| quartier_kreis      | string   | Quartier Kreis                  | Nummer Quartierkreis                                                                                         |        |
| quartier_quartiergr | string   | Quartiersgruppe                 | Quartiersgruppe                                                                                              |        |
| quartier_statistisc | string   | Statistisches Quartier          | Statistisches Quartier                                                                                       |        |

## Streetwise

### Method / Source

For information on Streetwise, please have a look at [streetwise.space](https://streetwise.space/about) or [Streetwise on GitHub](https://github.com/Streetwise).

### Data

#### Safety Score
- 📈 CSV: [data/streetwise/streetwise-safety.csv](data/streetwise/streetwise-safety.csv)
- 🗺 Styled GeoJSON: [snapshots/geojson/streetwise-safety.geojson](snapshots/geojson/streetwise-safety.geojson)
- 📦 Snapshot: [snapshots/streetwise-safety.json](snapshots/streetwise-safety.json)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**CSV Schema**

| name        | title                     | type    | description                                                   |
| ----------- | ------------------------- | ------- | ------------------------------------------------------------- |
| name        | Mapillary ID              | string  |                                                               |
| score       | Streetwise Safety Score   | number  |                                                               |
| description | Tooltip Text              | string  |                                                               |
| category    | Streetwise Score Category | integer |                                                               |
| label       | Streetwise Score Label    | string  |                                                               |
| _geom       | WKT geolocation           | string  | WKT representation of geo location                            |
| lat         | Latitude                  | string  | Latitude of source image rated with Streetwise Safety Score.  |
| lng         | Longitude                 | string  | Longitude of source image rated with Streetwise Safety Score. |

## Mobility

The following data is related to the temporary use [«Areal Bach»](https://areal-bach.ch) (Perimeter see [Snapshot](https://sandbox.dfour.space/de/0SF96/9CCGML/)) north the train station St. Fiden and shows aggregated origins and destination trips by postalcode of people coming to or from the area during the summer week of June 14–20 2021.

**Regular** in this context means multiple trips from the same origin/destination in the weeks before the sample is taken.

*Note*: Reference data for comparisons/context is available on request (find Viktoria or Thorben on the Discord).

Further background and information: [Swisscom Mobility Insights](https://mip.swisscom.ch).

### Data

#### Origin-Destination Matrix
- 📈 CSV: [data/mobility/od-mobility-matrix.csv](data/mobility/od-mobility-matrix.csv)
- 📦 Snapshot: [snapshots/10-inward_all.json](snapshots/10-inward_all.json)
- 📦 Snapshot: [snapshots/10-inward_regular.json](snapshots/10-inward_regular.json)
- 📦 Snapshot: [snapshots/10-inward_nonregular.json](snapshots/10-inward_nonregular.json)
- 📦 Snapshot: [snapshots/10-outward_all.json](snapshots/10-outward_all.json)
- 📦 Snapshot: [snapshots/10-outward_regular.json](snapshots/10-outward_regular.json)
- 📦 Snapshot: [snapshots/10-outward_nonregular.json](snapshots/10-outward_nonregular.json)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**CSV Schema**

| name               | type    | title                    | description                                                      |
| ------------------ | ------- | ------------------------ | ---------------------------------------------------------------- |
| ref_id             | integer | Reference ID             | Postalcode                                                       |
| inward_all         | integer | Inward trips             | All inward trips within the chosen week from ref_id.             |
| inward_nonregular  | integer | Inward trips nonregular  | All non regular inward trips within the chosen week from ref_id. |
| inward_regular     | integer | Inward trips regular     | All regular inward trips within the chosen week from ref_id.     |
| outward_all        | integer | Outward trips            | All outward trips within the chosen week to ref_id.              |
| outward_nonregular | integer | Outward trips nonregular | All non regular outward trips within the chosen week to ref_id.  |
| outward_regular    | integer | Outward trips regular    | All regular outward trips within the chosen week to ref_id.      |

#### Origin-Destination
- 📈 CSV: [data/mobility/od-mobility.csv](data/mobility/od-mobility.csv)

**CSV Schema**

| name       | type    | title              | description                                                 |
| ---------- | ------- | ------------------ | ----------------------------------------------------------- |
| ref_id     | integer | Reference ID       | Postalcode                                                  |
| ref        | integer | Reference          | Postalcode                                                  |
| count      | integer | Trips              | Sum of trips to/from ref_id within week_start and week_end. |
| week_start | date    | Week Start Date    | Date of survey start.                                       |
| week_end   | date    | Week Start Date    | Date of survey end.                                         |
| direction  | string  | Direction of Trips | inward (ref_id = origin) or outward (ref_id = destination)  |
| reason     | string  | Reason of Trips    | regular, non regular or both (all).                         |

#### Hourly
- 📈 CSV: [data/mobility/hourly.csv](data/mobility/hourly.csv)

**CSV Schema**

| name       | type     | title              | description                                                     |
| ---------- | -------- | ------------------ | --------------------------------------------------------------- |
| date       | datetime | Date and Time      |                                                                 |
| all        | integer  | Trips              | Sum of trips within `datetime` hour for `direction`             |
| nonregular | integer  | Non Regular Trips  | Sum of non regular trips within `datetime` hour for `direction` |
| regular    | integer  | Regular Trips      | Sum of regular trips within `datetime` hour for `direction`     |
| week_start |          | Week Start Date    | Date of survey start.                                           |
| week_end   |          | Week End Date      | Date of survey end.                                             |
| direction  |          | Direction of Trips | inward or outward                                               |

#### Daily
- 📈 CSV: [data/mobility/daily.csv](data/mobility/daily.csv)

**CSV Schema**

| name       | type     | title              | description                                                     |
| ---------- | -------- | ------------------ | --------------------------------------------------------------- |
| date       | datetime | Date               |                                                                 |
| all        | integer  | Trips              | Sum of trips within `datetime` day for `direction`             |
| nonregular | integer  | Non Regular Trips  | Sum of non regular trips within `datetime` day for `direction` |
| regular    | integer  | Regular Trips      | Sum of regular trips within `datetime` day for `direction`     |
| week_start |          | Week Start Date    | Date of survey start.                                           |
| week_end   |          | Week End Date      | Date of survey end.                                             |
| direction  |          | Direction of Trips | inward or outward                                               |

## Space Syntax

Further information on [Space Syntax Methodologies](https://library.oapen.org/handle/20.500.12657/50404).

### Data

#### Choice, Integration
- 📈 CSV: [data/spacesyntax/stgallen_region_choice_r5000.csv](data/spacesyntax/stgallen_region_choice_r5000.csv)

**CSV Schema**

| name                           | type    |
| ------------------------------ | ------- |
| Ref                            | integer |
| x1                             | number  |
| y1                             | number  |
| x2                             | number  |
| y2                             | number  |
| Angular Connectivity           | number  |
| Axial Line Ref                 | integer |
| Connectivity                   | integer |
| Segment Length                 | number  |
| T1024 Choice R1000 metric      | integer |
| T1024 Choice R2500 metric      | integer |
| T1024 Choice R500 metric       | integer |
| T1024 Choice R5000 metric      | integer |
| T1024 Integration R1000 metric | number  |
| T1024 Integration R2500 metric | number  |
| T1024 Integration R500 metric  | number  |
| T1024 Integration R5000 metric | number  |
| T1024 Node Count R1000 metric  | integer |
| T1024 Node Count R2500 metric  | integer |
| T1024 Node Count R500 metric   | integer |
| T1024 Node Count R5000 metric  | integer |
| T1024 Total Depth R1000 metric | number  |
| T1024 Total Depth R2500 metric | number  |
| T1024 Total Depth R500 metric  | number  |
| T1024 Total Depth R5000 metric | number  |

## For developers

Basic setup

```bash
# clone project
git clone git@github.com:cividi/st-gallen-urban-indicators.git
cd st-gallen-urban-indicators

# install virtual environment
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt

# setup environment variables
cp sample.env .env
# edit .env and add your details for postgresql database then activate it with
source .env
```

Run crawler
```bash
cd src && scrapy crawl homegate_spider
```

Run analysis and styling pipeline
```bash
cd src && python run_pipeline.py
```

## License

This package and most data sources are licensed by its maintainers under the CC BY 2.0 license.

If you intended to use these data in a public or commercial product, please check the data sources themselves for any specific restrictions, e.g. looking at the sources and licenses listed in [datapackage.json](datapackage.json).