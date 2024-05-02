import configparser
import logging
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from utils.clutch import find_companies

if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="a",
    filename="logs/mongodb.log",
)
config = configparser.ConfigParser()
config.read("secrets/config.ini")
username = config["mongodb"]["username"]
password = config["mongodb"]["password"]
app = config["mongodb"]["app"]
uri = f"mongodb+srv://{username}:{password}@crawled.abmyxjs.mongodb.net/?retryWrites=true&w=majority&appName={app}"
client = MongoClient(uri, server_api=ServerApi("1"))


def main(event, context):
    try:
        client.admin.command("ping")
        clutch = client["clutch"]
        links = clutch["links"]
        companies = clutch["companies"]
        for link in links.find({"link": {"$regex": "developer"}}):
            print(f"Processing link: {link['link']}")
            companies.insert_many(find_companies(link["link"]))
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}")
