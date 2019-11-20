#!/usr/bin/env python
# coding: utf-8

import requests
import csv
import time
import random

url_temp = 'https://www.zhihu.com/api/v4/members/%s/followees?include=data[*].follower_count&offset=%d&limit=20'
ids = {}
with open('node50.csv') as f:
    reader = csv.reader(f)
    for line in reader:
        ids[line[1]] = line[0]
print(ids)


h = {
    'host': 'www.zhihu.com',
#     'user-agent': '',  # 必要时需添加 user-agent和cookie
#     'cookie': ''
}
results = []
for uid in ids:
    print(uid, ids[uid])
    p = 0
    while True:
        url = url_temp % (uid, p*20)
        print(url)
        r = requests.get(url, headers=h)
    #     print(r.text)
        res = r.json()
        data = res['data']
        for d in data:
            if int(d['follower_count']) > 50:
                token = d['url_token']
                if token in ids:
                    results.append([ids[token], ids[uid]])
        time.sleep(1+random.random()*2)

        print(res['paging']['totals'])
        is_end = res['paging']['is_end']
        if is_end:
            print(results,'\n\n============\n\n\n')
            break
        else:
            p += 1


with open('edge50.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(results)

