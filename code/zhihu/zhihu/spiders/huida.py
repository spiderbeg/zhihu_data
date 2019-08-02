# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request # 调用请求
from zhihu.items import HuidaItem
import logging
import pymongo
import json
import time

class UserDataSpider(scrapy.Spider):
    name = 'huida'
    allowed_domains = ['zhihu.com']
    proxies = ["你的代理"] 
    header0 = { # chrome
        'user-agent': 'chrome',
        'cookie': '''你的知乎用户页面cookie'''
    }
    header1 = { # ie
        'user-agent': 'chrome',
        'cookie': '''你的知乎用户页面cookie'''    
    }
    header2 = { # SINODREAM
        'user-agent': 'chrome',
        'cookie': '''你的知乎用户页面cookie'''
    }
    headers = [header0,header1,header2]

    def start_requests(self):
        urls = []
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient['zhihu']
        mycol = mydb['user_info']
        myhp = mydb['user_answer_10w']
        ss = mycol.find({}) # url
        bb = myhp.find({}) # answer
        urls = []
        az,az2 = {},{}
        for i,s in enumerate(ss): # user_info
            nameid = s['user_id'] # 名字 id
            if '.' in s['user_id']:
                nameid = s['user_id'].replace('.','!---!')
            fs = s['user_info'][nameid]['followerCount'] # 粉丝数
            if fs >100000:
                az2[s['user_id']] = s['user_info'][nameid]['answerCount']
        for s in bb: # user_answer_10w
            az[s['author']['url_token']] = az.get(s['author']['url_token'], 0) + 1 

        for x in az2:
            if x not in az or az2[x] - az[x] > 5:
                urls.append(x)

        logging.log(logging.WARNING, "本次抓取个数{},抓取{}个用户，一共{}个用户".format(len(urls),len(az2),len(az))) # 自己打log

        for i2,user_id in enumerate(urls):
            c = i2%len(self.proxies)
            off = 0
            lim = 20
            u1 = "https://www.zhihu.com/api/v4/members/"
            u2 = "/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Clabel_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=" 
            url = u1 + user_id + u2 + str(off) + "&limit=" + str(lim) + "&sort_by=created"  
            logging.log(logging.WARNING, "用户顺序：第 {} 个，url: {}，IP：{} ".format(i2, url, self.proxies[c])) # 自己打log
            yield Request(url=url, callback=self.parse, dont_filter=True, headers=self.headers[c], meta={'proxy': self.proxies[c],'urlpi':[u1, user_id, u2, off, lim, c, i2],})

    def parse(self, response):
        r2 = json.loads(response.body_as_unicode()) # 转为json
        ip = response.meta['proxy']
        urlpi = response.meta['urlpi']
        off = int(urlpi[3]) + 20
        lim = str(urlpi[4])
        c = urlpi[5] + 1
        u1 = urlpi[0]
        user_id = urlpi[1]
        u2 = urlpi[2] 
        i2 = urlpi[6] # 爬取顺序
        if response.status == 403:
            logging.log(logging.WARNING, "状态码问题。用户{}，url: {}，IP：{} ".format(off,user_id, ip)) # 自己打log

        if 'data' in r2: 
            for d in r2['data']:
                item = HuidaItem()
                item = d
                yield item
        else:
            logging.log(logging.WARNING, "返回网页问题。用户{}，url: {}，IP：{} ".format(off,user_id, ip)) # 自己打log
            raise CloseSpider('回应的网页出现问题')

        if r2["paging"]['is_end'] == False:
            time.sleep(0.4)
            url = u1 + user_id + u2 + str(off) + "&limit=" + lim + "&sort_by=created" 
            logging.log(logging.WARNING, "用户回答数顺序：第 {} 页/20，url: {}.".format(off, url)) # 自己打log
            yield Request(url=url, callback=self.parse, dont_filter=True, headers=self.headers[c%len(self.headers)], meta={'proxy': self.proxies[c%len(self.proxies)],'urlpi':[u1, user_id, u2, off, lim, c, i2]})
        elif r2["paging"]['is_end'] == True:
            logging.log(logging.WARNING,"这个用户{}结束了, 顺序{}。".format(user_id, i2))
        else:
            logging.log(logging.WARNING,"一些意料之外的问题 {}".format(r2))
            raise CloseSpider('有情况我先看看')

