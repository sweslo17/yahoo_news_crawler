import pymongo
import utils
import os
import datetime
import time
from bs4 import BeautifulSoup


logger = utils.create_logger(__name__)
uri = os.environ.get("MONGO_URI")
client = pymongo.MongoClient(uri)
db = client["news"]

def get_new_pages(start_time):
    rs = db["news_page_raw"].find({
        "published_at": {"$gte": datetime.datetime.timestamp(start_time)}
        })
    new_dict = {r["id"]:r for r in rs}
    new_ids = list(new_dict.keys())
    rs = db["news_page_data"].find({})
    old_ids = [r["id"] for r in rs]
    diff_id_list = list(set(new_ids) - set(old_ids))
    return [(id, new_dict[id]["published_at"], new_dict[id]["html"]) for id in diff_id_list]

def parse_tags(soup):
    keywords_node = soup.find("meta",  attrs={"name":"news_keywords"})
    print(keywords_node)
    if keywords_node:
        keywords = keywords_node["content"].split(",")
        return [keyword.strip() for keyword in keywords]
    return []

def parse_htmls(page_list):
    for id, published_at, page in page_list:
        soup = BeautifulSoup(page, features="html.parser")
        tags = parse_tags(soup)
        db["news_page_data"].update_one({"id": id}, {"$set": {"published_at": published_at, "news_keywords": tags}}, upsert=True)

if __name__ == "__main__":
    while True:
        try:
            start_time = datetime.datetime.now() - datetime.timedelta(days=1)
            new_pages = get_new_pages(start_time)
            if new_pages:
                logger.info("Parse {} pages: {}.".format(len(new_pages), ", ".join([page[0] for page in new_pages])))
                parse_htmls(new_pages)
        except:
            logger.exception("Parse page error.")
        time.sleep(5)
