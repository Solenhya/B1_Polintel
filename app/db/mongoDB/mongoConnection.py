import os ,sys
import pymongo
project_dir = os.path.join(os.path.dirname(__file__), "..","..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    if os.getenv("MONGO_SIMPLE"):
        path = os.getenv("MONGO_SIMPLE")
    else:
        path = "mongodb://"+os.getenv("MONGO_USER")+":"+ os.getenv("MONGO_PASSWORD")+"@"+os.getenv("MONGO_HOST")
    return pymongo.MongoClient(path)
