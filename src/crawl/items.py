from scrapy import Field, Item


class RentalItem(Item):
    """ Defintion of rental price entries """

    id = Field()
    object_ref = Field()
    category = Field()
    date = Field()
    flatType = Field()
    floor = Field()
    rent = Field()
    rent_add = Field()
    rent_net = Field()
    rooms = Field()
    area = Field()
    year_built = Field()
    street_number = Field()
    city = Field()
    zip = Field()
    lat = Field()
    lng = Field()
    wkt = Field()
    egid = Field()
