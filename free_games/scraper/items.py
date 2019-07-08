import scrapy


class GameItem(scrapy.Item):
    title = scrapy.Field()
    store = scrapy.Field()
    url = scrapy.Field()
    img = scrapy.Field()
    startDate = scrapy.Field()
    endDate = scrapy.Field()
