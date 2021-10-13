import scrapy
import datetime
import requests
from urllib import parse

from ..items import RentalItem


class HomegateFlatSpider(scrapy.Spider):
    name = 'homegate_flats'
    url = "https://www.homegate.ch/rent/real-estate/zip-{}/matching-list?ep={}"


    def start_requests(self):
        for plz in range(8999, 9017):
            formatedUrl = self.url.format(plz, 1)
            yield scrapy.Request(url=formatedUrl, callback=self.parse)


    def parse(self, response):
        flats = response.css("a[class^='ListItem']")
        pageIndex = int(response.url[response.url.find("ep=") + 3:])
        plz = response.url[response.url.find("zip-") + 4:response.url.find("zip-") + 8]
        newPageIndex = pageIndex + 1

        if(len(flats) > 0):
            yield from response.follow_all(flats, self.parse_flat)
            yield scrapy.Request(url=self.url.format(plz, newPageIndex))
    
    def parse_flat(self, response):
        flat = RentalItem()

        try:
            details = response.css("div[class^='CoreAttributes_coreAttributes'] dd")
            details_labels = response.css("div[class^='CoreAttributes_coreAttributes'] dt ::text").getall()
            address = response.css("address[class^='AddressDetails_address'] span")
            cost = response.css("div[data-test^='cost'] dd span ::text")
            technical_info = response.css("dl[class^='ListingTechReferences_techReferencesList'] dd ::text")

            indexes = {
                "type": details_labels.index("Type:") if "Type:" in details_labels else None,
                "floor": details_labels.index("Floor:") if "Floor:" in details_labels else None,
                "rooms": details_labels.index("No. of rooms:") if "No. of rooms" in details_labels else None,
                "area": details_labels.index("Surface living:") if "Surface living:" in details_labels else None,
                "year_built": details_labels.index("Year built:") if "Year built:" in details_labels else None,
            }

            flat["id"] = int(response.url[response.url.find("rent/")+5:])
            flat["object_ref"] = technical_info[1].get()
            flat["category"] = "rent"
            flat["date"] = datetime.datetime.now().isoformat()
            flat['flatType'] = details[indexes["type"]].css("::text").extract_first() if indexes["type"] else None
            flat['floor'] = details[indexes["floor"]].css("::text").extract_first().replace(" ", "") if indexes["floor"] else None
            if len(cost) > 2:
                flat['rent'] = int(cost[5].get().replace(u'\u2013', "").replace(",", "").replace(".", ""))
                flat['rent_add'] = int(cost[3].get().replace(u'\u2013', "").replace(",", "").replace(".", "")) 
                flat['rent_net'] = int(cost[1].get().replace(u'\u2013', "").replace(",", "").replace(".", ""))
            else:
                flat['rent'] = int(cost[1].get().replace(u'\u2013', "").replace(",", "").replace(".", ""))
            flat['rooms'] = float(details[indexes["floor"]].get()) if indexes["rooms"] else None
            flat['area'] = int(details[indexes["area"]].css("::text").extract_first()) if indexes["area"] else None
            flat['year_built'] = int(details[indexes["year_built"]].css("::text").extract_first()) if indexes["year_built"] else None
            
            if len(address) > 1:
                flat['street_number'] = address[0].css("::text").extract_first().replace(",", "")[:-1]
                flat['city'] = address[1].css("::text").extract_first()[5:]
                flat['zip'] = address[1].css("::text").extract_first()[:4]
                flat["lat"], flat["lng"], flat["wkt"], flat["egid"] = geo_code_swisstopo(f"{flat['street_number']}, {flat['zip']} {flat['city']}")

            yield flat
        except Exception as e:
            self.log(e)

def geo_code_swisstopo(addressString=None):
    params = parse.urlencode(dict(
        type="locations",
        searchText=addressString,  # e.g. "Fähnernstrasse 3 9000 St. Gallen"
    ))

    url = f"https://api3.geo.admin.ch/rest/services/ech/SearchServer?{params}"

    res = requests.get(url)
    if res.status_code == 200:
        result = res.json()
        if "results" in result.keys() and len(result["results"]) > 0:
            likely_match = result["results"][0]["attrs"]
            return (likely_match['lat'], likely_match['lon'], f"POINT ({likely_match['lon']} {likely_match['lat']})", int(likely_match["featureId"]))
    
    return (None,None,None,None)