# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class ZhihuPipeline(object):
    ''' MongoDB 储存用户信息'''

    collection_name = 'user_info'
    huidaname = 'user_answer_10w'
    articlename = 'user_article_10w'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'))

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if spider.name == "user_data":
            if self.db[self.collection_name].find_one({'user_id':dict(item)['user_id']}):
                print('已存在, ', end="")
            else:
                # self.db[self.collection_name].insert_one(dict(item))
                print('0k', end='')
        elif spider.name == "huida":
            if self.db[self.huidaname].find_one({'id':dict(item)['id']}):
                print('已存在, ', end="")
            else:
                # self.db[self.huidaname].insert_one(dict(item))
                print('0k', end='')
        elif spider.name == "article":
            if self.db[self.articlename].find_one({'id':dict(item)['id']}):
                print('已存在, ', end="")
            else:
                self.db[self.articlename].insert_one(dict(item))
                print('0k', end='')
        return item


