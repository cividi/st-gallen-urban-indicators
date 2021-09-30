import scrapy
import datetime


class FlatSpider(scrapy.Spider):
    name = 'flats'
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

        yield {
            'id': response.url[response.url.find("rent/")+5:],
            'object_ref': technical_info[1].get(),
            'category': 'rent',
            'date': datetime.datetime.now().isoformat(),
            'type': details[indexes["type"]].css("::text").extract_first() if indexes["type"] else None,
            'floor': details[indexes["floor"]].css("::text").extract_first().replace(" ", "") if indexes["floor"] else None,
            'rent': int(cost[5].get().replace(u'\u2013', "").replace(",", "").replace(".", "")) if len(details) > 5 else int(cost[1].get().replace(u'\u2013', "").replace(",", "").replace(".", "")),
            'rent_add': int(cost[3].get().replace(u'\u2013', "").replace(",", "").replace(".", "")) if len(details) > 5 else None,
            'rent_net': int(cost[1].get().replace(u'\u2013', "").replace(",", "").replace(".", "")) if len(details) > 5 else None,
            'rooms': float(details[indexes["floor"]].get()) if indexes["rooms"] else None,
            'area': int(details[indexes["area"]].css("::text").extract_first()) if indexes["area"] else None,
            'year_built': int(details[indexes["year_built"]].css("::text").extract_first()) if indexes["year_built"] else None,
            'street_number': address[0].css("::text").extract_first().replace(",", "")[:-1],
            'city': address[1].css("::text").extract_first()[5:],
            'zip': address[1].css("::text").extract_first()[:4],
        }