import requests
import pymongo
import time
import random
import logging
import utils
import os


logger = utils.create_logger(__name__)
uri = os.environ.get("MONGO_URI")
client = pymongo.MongoClient(uri)
db = client["news"]

def get_list(start=0, count=100):
    output = []
    url = "https://tw.news.yahoo.com/_td-news/api/resource/IndexDataService.getExternalMediaNewsList;count={};loadMore=true;mrs=%7B%22size%22%3A%7B%22w%22%3A220%2C%22h%22%3A128%7D%7D;newsTab=all;start={};tag=null;usePrefetch=true"

    querystring = {"bkt":"news-TW-zh-Hant-TW-def","device":"desktop","feature":"videoDocking","intl":"tw","lang":"zh-Hant-TW","partner":"none","prid":"c98quplesb2hk","region":"TW","site":"news","tz":"Asia/Taipei","ver":"2.3.1296","returnMeta":"true"}

    headers = {
        'cache-control': "no-cache",
        'postman-token': "e6bec066-b8dc-db29-8b81-da537c31a3f4"
        }

    response = requests.request("GET", url.format(count, start), headers=headers, params=querystring)

    if response:
        news_list = response.json()["data"]
        for news in news_list:
            r = db["news_list"].find_one({"id": news["id"]})
            if not r:
                db["news_list"].insert_one(news)
                output.append(news["id"])
    
    return output

if __name__ == "__main__":
    while True:
        try:
            new_id_list = get_list()
            if len(new_id_list) > 0:
                logger.info("Got {} ids: {}.".format(len(new_id_list), ", ".join(new_id_list)))
        except:
            logger.exception("Get id list error.")
        time.sleep(random.randint(1,5))