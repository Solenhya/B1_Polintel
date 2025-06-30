import requests
import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)

from dotenv import load_dotenv
load_dotenv()
dbName = os.getenv("MONGO_DBNAME")

from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from sqlalchemy import select
from db.postgreSQL.models import DeclarationMoney

import logging
logger = logging.getLogger(__name__)

# Creer le handler de fichier
file_handler = logging.FileHandler('import_declaration_finance.log')
file_handler.setLevel(logging.DEBUG)

# Creer un formateur et le rajoute au handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# rajoute le handler sur le logger
logger.addHandler(file_handler)

from tqdm import tqdm
from bs4 import BeautifulSoup
from utils.json_import import jsondata_from_xml
from utils.db_import import get_count_doc_left
from datetime import datetime
from scrapping.scrappinghatvp import recuperate_data


def proccess_all():
    nom_operation="import_declaration_monetaire"
    with mongoConnection.get_connection() as client:
            with db_connection.get_session() as session:
                collection= client[dbName]["acteur"]
                query = {f"_traitement.{nom_operation}":{"$exists":0}}
                total = get_count_doc_left(collection,nom_operation)
                success = 0
                nomComplet="Importation des declarations d'interet et patrimoine deputé"
                currentDate = datetime.now()
                for data in tqdm(collection.find(query),total=total,desc=nomComplet):
                    url = data["uri_hatvp"]
                    id = data["_id"]
                    try:
                        recuperate_data(url,id,session,currentDate)
                        queryName = f"_traitement.{nom_operation}"
                        data = {"date":currentDate,"status":"Success"}
                        collection.update_one(
                        {"_id": id},
                        {"$set": {queryName: data}}
                        )
                        success+=1
                    except Exception as e:
                        logger.error(f"Erreur dans l'import d'une déclaration financiere de député sur le député : {id};Erreur : {e}")
                        session.rollback()
    return success,total
        

if __name__=="__main__":
    proccess_all()