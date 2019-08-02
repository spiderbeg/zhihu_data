# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request # 调用请求
from zhihu.items import ZhihuItem
import logging
import pymongo
from bs4 import BeautifulSoup
import json

class UserDataSpider(scrapy.Spider):
    name = 'user_data'
    allowed_domains = ['zhihu.com']

    def start_requests(self):
        proxies = ["你的代理"]
        urls = []
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient['zhihu']
        mycol = mydb['user_pd']
        myhp = mydb['user_info']
        ss = mycol.find({}) # url
        dd = myhp.find({})
        used = {1,}
        usedz = {}
        for d in dd:
            used.add(d['user_id'])
        for i,s in enumerate(ss):
            if 0<=i:
                usedz[s['user_id']] = usedz.get(s['user_id'], 0) + 1
                if s['follower_count']>=10000 and usedz[s['user_id']]==1: # 粉丝数大于10000
                    urls.append(s['user_id'])
            # elif i>1500000:
            #     break
        logging.log(logging.WARNING, "开始处...；总个数 {}".format(len(urls))) # 自己打log

        for i2,urlid in enumerate(urls):
            if urlid in used: # 是否使用过
                continue
            c = i2%len(proxies)
            url = 'https://www.zhihu.com/people/' + urlid + '/activities'
            logging.log(logging.WARNING, "顺序：第 {} 个，url: {}，IP：{} ".format(i2, url, proxies[c])) # 自己打log
            yield Request(url=url, callback=self.parse, dont_filter=True, meta={'proxy': proxies[c],'url':urlid})

    def parse(self, response):
        user_id = response.meta['url']
        soup = BeautifulSoup(response.body, features="lxml")
        res6 = soup.find_all(id='js-initialData')[0]
        total = json.loads(res6.string) # 反序列化为 dict
        resultj = total['initialState']['entities']['users']
        if '.' in user_id: # 含有 .
            pro = resultj.copy() # 复制 
            resultj.pop(user_id)
            for ke in pro:
                if ke == user_id:
                    ks = ke.replace('.','!---!')
                    resultj[ks] = pro[ke].copy() 
        if len(resultj)==1:
            raise NameError('页面错误')
        # print('kjhjkhkhk',resultj)
        result = {}
        result['user_info'] = resultj
        result['user_id']  = user_id
        # print(user_id)
        item = ZhihuItem()
        item = result

        yield item

