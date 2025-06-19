import os,sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Remonte jusqu'au dossier parent
sys.path.append(parent_dir)

from dotenv import load_dotenv
load_dotenv()
from app.db.mongoDB import mongoConnection

from app.utils.db_import import get_count_doc_left

def testcount():
    with mongoConnection.get_connection() as client:
        collection = client["test"]["test"]
        count = get_count_doc_left(collection,"insertion_traite")
        assert count == 1