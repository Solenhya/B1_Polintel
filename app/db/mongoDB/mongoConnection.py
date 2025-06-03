import os
import pymongo

def get_connection():
    path = "mongodb://"+os.getenv("MONGO_USER")+":"+ os.getenv("MONGO_PASSWORD")+"@"+os.getenv("MONGO_HOST")
    return pymongo.MongoClient(path)
