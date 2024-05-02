from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import configparser
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="a",
    filename="logs/mongodb.log",
)

config = configparser.ConfigParser()
config.read('secrets/config.ini')

username = config['mongodb']['username']
password = config['mongodb']['password']
app = config['mongodb']['app']
uri = f"mongodb+srv://{username}:{password}@crawled.abmyxjs.mongodb.net/?retryWrites=true&w=majority&appName={app}"
client = MongoClient(uri, server_api=ServerApi('1'))

if __name__ == "__main__":
    try:
        client.admin.command('ping')
        db = client['clutch']
        collection = db['agency']
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {str(e)}")