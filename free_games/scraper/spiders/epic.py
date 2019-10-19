import json
import scrapy
from scraper.items import GameItem


class EpicSpider(scrapy.Spider):
    name = 'epic'
    allowed_domains = ['graphql.epicgames.com/graphql/']

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
    bundle_query = """
    query catalogQuery($productNamespace:String!, $offerId:String!, $locale:String, $country:String!) {
        Catalog {
            catalogOffer(namespace: $productNamespace, id: $offerId, locale: $locale) {
                title
                collectionOffers {
                    title
                    id
                    namespace
                    description
                    keyImages {
                        type
                        url
                    }
                    items {
                        id
                        namespace
                    }
                    customAttributes {
                        key
                        value
                    }
                    categories {
                        path
                    }
                    price(country: $country) {
                        totalPrice {
                            discountPrice
                            originalPrice
                            voucherDiscount
                            discount
                            fmtPrice(locale: $locale) {
                                originalPrice
                                discountPrice
                                intermediatePrice
                            }
                        }
                    }
                    linkedOfferId
                    linkedOffer {
                        effectiveDate
                        customAttributes {
                            key
                            value
                        }
                    }
                }
            }
        }
    }
    """
    data = {"query": query, "variables": {"namespace": "epic", "country": "US"}}
    bundle_data = {"query": bundle_query, "variables": {"productNamespace": "epic", "country": "US"}}

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
            start_date = None
            end_date = None
            if element.get('promotions'):
                for i, promotion in element.get('promotions', {}).items():
                    if len(promotion) != 0:
                        start_date = promotion[0].get('promotionalOffers', [])[0].get('startDate', '')
                        end_date = promotion[0].get('promotionalOffers', [])[0].get('endDate', '')
            else:
                continue 

            if 'collection' in element.get('productSlug', {}):
                self.bundle_data['variables']['offerId'] = element.get('id', {})
                yield scrapy.Request("https://graphql.epicgames.com/graphql/",
                                     method='POST',
                                     body=json.dumps(self.bundle_data),
                                     callback=self.parse_bundle,
                                     headers={"Content-type": "application/json"},
                                     cb_kwargs={'start_date': start_date, 'end_date': end_date},
                                     dont_filter=True)
            else:
                image_coming_soon = None
                image_logo = None
                image_wide = None

                for image in element.get('keyImages'):
                    if image.get('type') == 'ComingSoon':
                        image_coming_soon = image.get('url')

                game_data = GameItem()

                game_data['title'] = element.get('title')
                game_data['store'] = 'Epic'
                game_data['url'] = 'https://www.epicgames.com/store/en-US/product/{}'.format(element.get('productSlug'))
                game_data['img_coming_soon'] = image_coming_soon
                game_data['img_logo'] = image_logo
                game_data['img_wide'] = image_wide
                game_data['startDate'] = start_date
                game_data['endDate'] = end_date

                yield game_data

    def parse_bundle(self, response, start_date, end_date):
        data = json.loads(response.text).get('data', {})
        elements = data.get('Catalog', {}).get('catalogOffer', {}).get('collectionOffers', {})
        for element in elements:
            image_coming_soon = None
            image_logo = None
            image_wide = None

            for image in element.get('keyImages'):
                if image.get('type') == 'DieselGameBoxLogo':
                    image_logo = image.get('url')
                elif image.get('type') == 'DieselStoreFrontWide':
                    image_wide = image.get('url')

            game_data = GameItem()

            game_data['title'] = element.get('title')
            game_data['store'] = 'Epic'
            game_data['url'] = 'https://www.epicgames.com/store/en-US/product/{}'\
                .format(element.get('customAttributes')[3].get('value'))
            game_data['img_coming_soon'] = image_coming_soon
            game_data['img_logo'] = image_logo
            game_data['img_wide'] = image_wide
            game_data['startDate'] = start_date
            game_data['endDate'] = end_date

            yield game_data
