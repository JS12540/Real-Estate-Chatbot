import pymongo
import os

client = pymongo.MongoClient(os.getenv("MONGODB_CONNECTION_URI"))

database = client[os.getenv("MONGODB_DATABASE_NAME")]

cache = database["cache"]