# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TenementItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    rental = scrapy.Field()
    lease_way = scrapy.Field()
    house_type = scrapy.Field()
    toward_floor = scrapy.Field()
    housing_estate = scrapy.Field()
    region = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
