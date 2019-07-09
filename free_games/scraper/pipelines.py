from pymongo import MongoClient, ASCENDING, errors
from scrapy.exceptions import DropItem


class MongoPipeline(object):
    collection_name = 'game_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB', 'items')
        )

    def open_spider(self, spider):
        """
        Setup the DB client and creates an index to avoid duplicates if it doesn't exist already.
        """
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].create_index([
                                                    ('title', ASCENDING),
                                                    ('store', ASCENDING),
                                                    ('url', ASCENDING),
                                                    ('img', ASCENDING),
                                                    ('startDate', ASCENDING),
                                                    ('endDate', ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(dict(item))
            return item
        except errors.DuplicateKeyError:
            raise DropItem('This item already exists : {}, {}'.format(item['title'], item['store']))

