import scrapy


class GameItem(scrapy.Item):
    title = scrapy.Field()
    store = scrapy.Field()
    url = scrapy.Field()
    img_wide = scrapy.Field()
    img_logo = scrapy.Field()
    img_coming_soon = scrapy.Field()
    startDate = scrapy.Field()
    endDate = scrapy.Field()
