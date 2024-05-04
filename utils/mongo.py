import configparser

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

config = configparser.ConfigParser()
config.read("secrets/config.ini")
uri = f'mongodb+srv://{config["mongodb"]["username"]}:{config["mongodb"]["password"]}@crawled.abmyxjs.mongodb.net/?retryWrites=true&w=majority&appName={config["mongodb"]["app"]}'
client = MongoClient(uri, server_api=ServerApi("1"))
