import os
import pymongo

def get_connection():
    if os.getenv("MONGO_SIMPLE"):
        path = os.getenv("MONGO_SIMPLE")
    else:
        path = "mongodb://"+os.getenv("MONGO_USER")+":"+ os.getenv("MONGO_PASSWORD")+"@"+os.getenv("MONGO_HOST")
    return pymongo.MongoClient(path)
