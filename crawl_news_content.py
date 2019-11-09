import requests
import pymongo
from urllib.parse import quote
import time
import datetime
import random
import json
import utils
import os


logger = utils.create_logger(__name__)
uri = os.environ.get("MONGO_URI")
client = pymongo.MongoClient(uri)
db = client["news"]

def get_new_ids():
    rs = db["news_list"].find({})
    new_ids = [r["id"] for r in rs]
    rs = db["news_data"].find({})
    old_ids = [r["uuid"] for r in rs]
    return list(set(new_ids) - set(old_ids))

def get_content(id_list, replace=False):
    url = "https://tw.news.yahoo.com/_td-news/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=news;uuids={}"

    querystring = {"bkt":"news-TW-zh-Hant-TW-def","device":"desktop","feature":"videoDocking","intl":"tw","lang":"zh-Hant-TW","partner":"none","prid":"c98quplesb2hk","region":"TW","site":"news","tz":"Asia/Taipei","ver":"2.3.1296","returnMeta":"true"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "daa16e5c-6b90-f161-0dd3-465bda4dcc08"
        }
    for i in range(0, int(len(id_list)/10)+1):
        response = requests.request("GET", url.format(quote(json.dumps(id_list[i*10:(i+1)*10]))), headers=headers, params=querystring)
        response.raise_for_status()
        if response:
            items = response.json()["data"]["items"]
            for item in items:
                if "publishDate" in item:
                    item["publish_datetime"] = datetime.datetime.strptime(item["publishDate"], "%a, %d %b %Y %H:%M:%S %Z")
            db["news_data"].insert_many(items)
        time.sleep(random.randint(1,5))

if __name__ == "__main__":
    while True:
        try:
            id_list = get_new_ids()
            if id_list:
                logger.info("Crawling {} content: {}.".format(len(id_list), ", ".join(id_list)))
                get_content(id_list)
                logger.info("Crawl done.")
        except:
            logger.exception("Crawl content error.")
        time.sleep(5)