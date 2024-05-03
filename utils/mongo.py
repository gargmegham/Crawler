import configparser
import logging
import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from selenium import webdriver

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


if __name__ == "__main__":
    try:
        client.admin.command("ping")
        clutch = client["clutch"]
        companies = clutch["companies"]
        driver = webdriver.Chrome()
        for company in companies.find(
            {"website_link": {"$exists": True}, "linkedin_links": {"$exists": False}}
        ):
            pass
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}", exc_info=True)
    finally:
        driver.quit()
        client.close()
