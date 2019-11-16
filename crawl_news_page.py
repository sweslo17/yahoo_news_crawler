import requests
import pymongo
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

def get_new_urls(start_time):
    rs = db["news_list"].find({
        "published_at": {"$gte": datetime.datetime.timestamp(start_time)},
        "url": {"$exists": True}
        })
    new_dict = {r["id"]:r for r in rs}
    new_ids = list(new_dict.keys())
    rs = db["news_page_raw"].find({})
    old_ids = [r["id"] for r in rs]
    diff_id_list = list(set(new_ids) - set(old_ids))
    return [(new_dict[id]["url"], id, new_dict[id]["published_at"]) for id in diff_id_list]

def get_pages(url_list, replace=False):
    base_url = "https://tw.news.yahoo.com{}"

    for url, id, published_at in url_list:
        response = requests.request("GET", base_url.format(url))
        response.raise_for_status()
        if response:
            db["news_page_raw"].insert_one({
                "id": id,
                "url": url,
                "published_at": published_at,
                "html": response.text
            })
        time.sleep(random.randint(1,3))

if __name__ == "__main__":
    while True:
        try:
            start_time = datetime.datetime.now() - datetime.timedelta(days=10)
            new_urls = get_new_urls(start_time)
            logger.info("Crawling {} page: {}.".format(len(new_urls), ", ".join([url[1] for url in new_urls])))
            get_pages(new_urls)
        except:
            logger.exception("Crawl page error.")
        time.sleep(5)
    