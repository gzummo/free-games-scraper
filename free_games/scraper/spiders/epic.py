import json
import scrapy
from scraper.items import GameItem


class EpicSpider(scrapy.Spider):
    name = 'epic'
    allowed_domains = ['graphql.epicgames.com/graphql']

    query = """
    query promotionsQuery($namespace: String!, $country: String!) {
        Catalog {
            catalogOffers(namespace: $namespace, params: {category: \"freegames\", country: $country, sortBy: \"effectiveDate\", sortDir: \"asc\"}) {
                elements {
                    title
                    description
                    id
                    namespace
                    linkedOfferNs
                    linkedOfferId
                    keyImages {
                        type
                        url
                    }
                    productSlug
                    promotions {
                        promotionalOffers {
                            promotionalOffers {
                                startDate
                                endDate
                                discountSetting {
                                    discountType
                                    discountPercentage
                                }
                            }
                        }
                        upcomingPromotionalOffers {
                            promotionalOffers {
                                startDate
                                endDate
                                discountSetting {
                                    discountType
                                    discountPercentage
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    data = {"query": query, "variables": {"namespace": "epic", "country": "US"}}

    def start_requests(self):
        yield scrapy.http.Request("https://graphql.epicgames.com/graphql/",
                                  method='POST',
                                  body=json.dumps(self.data),
                                  callback=self.parse,
                                  headers={"Content-type": "application/json"})

    def parse(self, response):
        data = json.loads(response.text).get('data', {})
        elements = data.get('Catalog', {}).get('catalogOffers', {}).get('elements', {})

        for element in elements:
            image_url = None
            start_date = None
            end_date = None

            for image in element.get('keyImages'):
                if image.get('type') == 'ComingSoon':
                    image_url = image.get('url')
                    break

            for i, promotion in element.get('promotions').items():
                if len(promotion) != 0:
                    start_date = promotion[0].get('promotionalOffers')[0].get('startDate')
                    end_date = promotion[0].get('promotionalOffers')[0].get('endDate')

            game_data = GameItem()

            game_data['title'] = element.get('title')
            game_data['store'] = 'Epic'
            game_data['url'] = 'https://www.epicgames.com/store/en-US/product/{}'.format(element.get('productSlug'))
            game_data['img'] = image_url
            game_data['startDate'] = start_date
            game_data['endDate'] = end_date

            yield game_data
