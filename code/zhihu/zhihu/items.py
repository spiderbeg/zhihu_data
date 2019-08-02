# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_info = scrapy.Field()

class HuidaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_huida = scrapy.Field()

class ArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    user_huida = scrapy.Field()
