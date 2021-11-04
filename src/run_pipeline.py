import json
from datetime import datetime
from frictionless import Resource, Package, Layout, transform, steps
from frictionless.plugins.sql import SqlDialect
from crawl.models import Items, Addresses, GWR_WHG, db_connect
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from crawl import settings

engine = db_connect()
session_ = sessionmaker(bind=engine)
session = session_()

## 1. Fill geocoding gaps by fuzzy matching to GWR entries

res = session.query(Items).filter(Items.wkt.is_(None)).all()
for r in res:
    if r.street_number:
        zip_string = f"{r.zip} {r.city}"
        address_string = f"{r.street_number}, {zip_string}"
        match = session.query(Addresses).with_entities(
            Addresses.egid, Addresses.geom, func.SIMILARITY(address_string, Addresses.address_string)
        ).filter(
            and_(Addresses.zipcode == zip_string, func.SIMILARITY(address_string, Addresses.address_string) > 0.6)
        ).order_by(
            (func.SIMILARITY(address_string, Addresses.address_string)).desc()
        ).limit(1).one_or_none()

        if match:
            try:
                session.query(Items).filter_by(id = r.id).update({Items.wkt: match.geom, Items.egid : match.egid})
                session.commit()
                print(f"{r.id} updated: {match}")
            except:
                session.rollback()
                print("An error occured")

db_string = f"{settings.DATABASE['drivername']}://{settings.DATABASE['username']}:{settings.DATABASE['password']}@{settings.DATABASE['host']}:{settings.DATABASE['port']}/{settings.DATABASE['database']}"


### 2. Add data from GWR on apartment area, rooms and floor by heuristically matching flat inside building obtained by geocoding (see 1)

def get_gwr_data(egid, area, stwk):
    if egid:
        if str(egid)[-1:] == "0":
            egid = egid / 10
        if stwk and (str(stwk).isdigit() or stwk == "GF"):
            if str(stwk).isdigit():
                floor = int(stwk)
            elif stwk == "GF":
                floor = 0
            
            match = session.query(GWR_WHG).with_entities(
                GWR_WHG.egid, GWR_WHG.edid, GWR_WHG.wazim, GWR_WHG.warea, GWR_WHG.wstwk, func.delta(area,GWR_WHG.warea)
            ).filter(
                and_(GWR_WHG.egid == int(egid), GWR_WHG.wstwk == int(f"310{floor}"))
            ).order_by(
                func.delta(area,GWR_WHG.warea)
            ).limit(1)
        else:
            match = session.query(GWR_WHG).with_entities(
                GWR_WHG.egid, GWR_WHG.edid, GWR_WHG.wazim, GWR_WHG.warea, GWR_WHG.wstwk, func.delta(area,GWR_WHG.warea)
            ).filter(
                GWR_WHG.egid == int(egid)
            ).order_by(
                func.delta(area,GWR_WHG.warea)
            ).limit(1)

        if match.one_or_none():
            return match.one_or_none()
    
    return (None, None, None, None, None, None)

enriched = transform(
    Resource(
        path=db_string,
        dialect=SqlDialect(
            namespace=settings.DATABASE_PG_SCHEMA,
            table="prices",
        )
    ),
    steps=[
        steps.field_add(name="gwr_egid", function=lambda x: get_gwr_data(x["egid"], x["area"], x["floor"])[0]),
        steps.field_add(name="gwr_wazim", function=lambda x: get_gwr_data(x["egid"], x["area"], x["floor"])[2]),
        steps.field_add(name="gwr_warea", function=lambda x: get_gwr_data(x["egid"], x["area"], x["floor"])[3]),
        steps.field_add(name="gwr_wstwk", function=lambda x: get_gwr_data(x["egid"], x["area"], x["floor"])[4]),
        steps.field_add(name="match_accuracy", function=lambda x: get_gwr_data(x["egid"], x["area"], x["floor"])[5]),
        steps.table_write(path="data/price-monitoring/price-monitoring.csv")
    ]
)

### 3. Classify and Style data

res = Resource("data/price-monitoring/price-monitoring.csv")

categories_flat = [
    { "from": 1, "to": 3, "cat": "S"},
    { "from": 3, "to": 5, "cat": "M"},
    { "from": 5, "to": 20, "cat": "L"},
]

categories = [
    { "from": 0, "to": 150, "cat": "a"},
    { "from": 150, "to": 300, "cat": "b"},
    { "from": 300, "to": 450, "cat": "c"},
    { "from": 450, "to": 600, "cat": "d"},
    { "from": 600, "to": 750, "cat": "e"},
    { "from": 750, "to": 2000, "cat": "f"},
]

colors = {
    "a": { "fillColor": "#0028b8", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
    "b": { "fillColor": "#455db5", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
    "c": { "fillColor": "#8a93b2", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
    "d": { "fillColor": "#bfa98f", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
    "e": { "fillColor": "#df9848", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
    "f": { "fillColor": "#ff8800", "fillOpacity": 0.8, "color": "#ffffff", "weight": 1.5, "opacity": 0.9, "radius": 45 },
}

def category_mapping(value, mappings):
    if len(mappings) > 0:
        for mapping in mappings:
            if "from" in mapping.keys() and "to" in mapping.keys() and "cat" in mapping.keys():
                if value >= mapping["from"] and value < mapping["to"]:
                    return mapping["cat"]
    return None

def color_mapping(value, mapping, key):
    if value in mapping.keys():
        if key in mapping[value].keys():
            return mapping[value][key]
    return None


styled = transform(
    "data/price-monitoring/price-monitoring.csv",
    steps=[
        steps.row_filter(formula="area is not ''"),
        steps.row_filter(formula="gwr_warea is not ''"),
        steps.row_filter(formula="gwr_wazim is not ''"),
        steps.row_filter(formula="int(area) > 20"),
        steps.table_normalize(),
        steps.field_add(name="price_per_sqm", type="number", formula="int(rent) / int(area)"),
        steps.field_add(name="price_per_room", type="number", formula="int(rent) / int(gwr_wazim)"),
        steps.table_normalize(),
        steps.field_add(name="flat_cat", type="string", function=lambda x: category_mapping(x["gwr_wazim"], categories_flat)),
        steps.field_add(name="cat", type="string", function=lambda x: category_mapping(x["price_per_room"], categories)),
        steps.table_write(path="data/price-monitoring/price-monitoring.csv"),
        steps.table_normalize(),
        steps.field_add(name="fillColor", type="string", function=lambda x: color_mapping(x["cat"], colors, "fillColor")),
        steps.field_add(name="fillOpacity", type="number", function=lambda x: color_mapping(x["cat"], colors, "fillOpacity")),
        steps.field_add(name="color", type="string", function=lambda x: color_mapping(x["cat"], colors, "color")),
        steps.field_add(name="weight", type="number", function=lambda x: color_mapping(x["cat"], colors, "weight")),
        steps.field_add(name="opacity", type="number", function=lambda x: color_mapping(x["cat"], colors, "opacity")),
        steps.field_add(name="radius", type="integer", function=lambda x: color_mapping(x["cat"], colors, "radius")),
        steps.field_update(name="wkt", new_name="_geom"),
        steps.table_normalize(),
        steps.table_write(path="data/price-monitoring/homegate-styled.csv"),
    ]
)

### 4. Export as spatial data package (see https://github.com/cividi/spatial-data-package)

legend_addendum = {
    "S": "1-2 Zimmer",
    "M": "3-4 Zimmer",
    "L": "5+ Zimmer",
}

for size in ["S","M","L"]:
    data = transform(
        Resource("data/price-monitoring/homegate-styled.csv"),
        steps = [
            steps.table_normalize(),
            steps.field_update(name="_geom", type="string"),
            steps.row_filter(function=lambda x: x['flat_cat'] == size),
            steps.field_add(name="title", type="string", function=lambda x: f"Wohnung '{size}'"),
            steps.field_add(name="description", type="string", function=lambda x: f"Miete: {x['rent']} CHF/Monat<br>Miete/qm: {round(x['price_per_sqm'],2)} CHF/Monat<br>Miete/Zimmer: {round(x['price_per_room'],2)} CHF/Monat<br>Nebenkosten: {x['rent_add']} CHF/Monat"),
            steps.table_normalize(),
        ]
    )
    data.write(path=f"snapshots/geojson/homegate-styled-{size}.geojson")

    styled.name = "data"
    styled["mediatype"] = "application/vnd.simplestyle-extended"
    with open(f"snapshots/geojson/homegate-styled-{size}.geojson") as json_file:
        styled.data = json.load(json_file)
    styled

    background_map = dict(
        name="mapbox-background",
        path = "mapbox://styles/gemeindescan/ckv9xyllc00g215o8bjnh6cmo",
        mediatype = "application/vnd.mapbox-vector-tile",
    )

    ## Built package

    pkg = Package(
        name=f"01-rent-prices-{size}",
        resources=[
            styled, background_map
        ],
        sources=[
            {
                "url": "https://homegate.ch",
                "title": "Homegate",
            },
            {
                "title": "Karte: Mapbox, © OpenStreetMap",
                "url": "https://www.openstreetmap.org/copyright"
            },
        ]
    )

    pkg["views"] = [
            {
                "name": "mapview",
                "resources": [
                    "mapbox-background",
                    "data",
                ],
                "spec": {
                    "attribution": "",
                    "bounds": [
                        "geo:47.41525506820663,9.352516279706524",
                        "geo:47.43317355684985,9.396247605270359"
                    ],
                    "title": f"Mietpreise Wohnungen {size}",
                    "description": f"Mietpreise Stadt St. Gallen Wohnungen {size} ({legend_addendum[size]}), Daten: 12.10.2021 - {datetime.strftime(datetime.today(),'%d.%m.%Y')}.",
                    "legend": [
                        {
                            "fillColor": "#0028b8",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "60-149 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#455db5",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "150-299 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#8a93b2",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "300-449 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#bfa98f",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "450-599 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#df9848",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "600-749 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#ff8800",
                            "fillOpacity": 0.8,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0.9,
                            "strokeWidth": 1.5,
                            "size": 1,
                            "shape": "circle",
                            "primary": True,
                            "label": "750-1750 CHF/Zimmer",
                        },
                        {
                            "fillColor": "#c51b1b",
                            "fillOpacity": 1,
                            "strokeColor": "#ffffff",
                            "strokeOpacity": 0,
                            "strokeWidth": 0,
                            "size": 1,
                            "shape": "square",
                            "primary": True,
                            "label": "Gebäude über Lärmimmissionsgrenzwert",
                        },
                    ]
                },
                "specType": "gemeindescanSnapshot"
            }
        ]

    with open(f"snapshots/01-rent-prices-{size}.json", "w") as pkg_file:
        json.dump(pkg, pkg_file, indent=2)

# cleanup for publication

transform(
    Resource(path="data/price-monitoring/price-monitoring.csv"),
    steps=[
        steps.field_remove(names=["gwr_wazim","gwr_warea","gwr_wstwk", "egid"]),
        steps.table_write(path="data/price-monitoring/price-monitoring.csv"),
    ]
)

# Adding noise and quartier columns

buildings = Resource(
    path="data/misc/stgallen-buildings.geojson",
    layout=Layout(pick_fields=["egid","ren_potential","quartier_nummer","quartier_kreis","quartier_quartiergr","quartier_statistisc","LR_DAY","LR_NIGHT","ES","COMM_USE_D","EXP_LIM_D","EXP_LIM_N","EXP_LIM","noise_below"])
).to_pandas()

prices = Resource(path="data/price-monitoring/price-monitoring.csv").to_pandas()
joined = prices.merge(buildings, left_on="gwr_egid", right_on="egid", how="left")
joined.to_csv("data/price-monitoring/price-monitoring-extended.csv", index=False)

## Write GeoJSON version

gjson = transform(
    joined,
    steps=[
        steps.field_update(name="wkt", new_name="_geom"),
    ]
)

gjson.write(path="data/price-monitoring/price-monitoring-extended.geojson")
