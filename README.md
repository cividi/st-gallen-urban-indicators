[![publish to dfour](https://github.com/cividi/st-gallen-urban-indicators/actions/workflows/sync.yaml/badge.svg)](https://github.com/cividi/st-gallen-urban-indicators/actions/workflows/sync.yaml)

# Urban Indicators St. Gallen

A work in progress repository collecting data, links to datasets and analysis for indicators on

- rental prices
- public space qualities
- imissions like noise and air quality

Output maps: [https://sandbox.dfour.space/de/0SF96/M3JDL6/](https://sandbox.dfour.space/de/0SF96/M3JDL6/)

## Rental Prices

### Method

In broad strokes the collection and analysis of rent prices follows the following steps
1. Incremental (Crawler) collection of advertisements from public portals, e.g. Homegate into a PostgreSQL database and geocoding addresses with [Swisstopo REST Service](https://api3.geo.admin.ch/services/sdiservices.html#search)
2. Periodically (GitHub Action)
   - enriching the collected entries with official area, floor, building year from [housing data](https://www.housing-stat.ch) through heuristically matching housing portal entries to registered apartments
   - Calculating rent per room and per square meter
   - Group apartments by "size class" depending on number of rooms

Python frameworks and libraries used: [scrapy](https://docs.scrapy.org/en/latest/index.html), [frictionless-py](https://framework.frictionlessdata.io), [sqlalchemy](https://docs.sqlalchemy.org/en/14/)

### Data

The data can be found in [`data/price-monitoring/price-monitoring.csv`](data/price-monitoring/price-monitoring.csv).

### Developer

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

