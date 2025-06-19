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
        

def recuperate_data(url,hopol_id,session,dateTraitement):
    requete = requests.get(url)
    soup = BeautifulSoup(requete.text,"html.parser")
    interet = recuperation_info(soup,hopol_id,"interet",dateTraitement)
    patrimoine = recuperation_info(soup,hopol_id,"patrimoine",dateTraitement)
    session.merge(interet)
    session.commit()
    session.merge(patrimoine)
    session.commit()

def recuperation_info(soup,hopolId,recuperation,dateTraitement):
    with mongoConnection.get_connection() as client:
        collection = client[dbName]["declaration_money"]
        section = soup.find('section', id=recuperation)
        listUrl = get_list_url(section)
        type_declar = recuperation
        if len(listUrl)>0:
            status = "Publie et accessible en ligne"
            mongoId = create_mongo(listUrl[0],collection,recuperation)
            declaration = create_declare(hopolId,type_declar,dateTraitement,status=status,mongoId=mongoId)
            return declaration
        else:
            info = section.find("p",class_="info-declaration")
            if(not info):
                logger.error(f"Erreur dans la récuperation d'information de scraping l'element 'info-declaration' n'est pas présent")
                return
            infoText = info.text.strip()
            declaration = create_declare(hopolId,type_declar,dateTraitement,infoText,None)
            return declaration


def get_access(infoText):
    if infoText=="Déclaration déposée - publication à venir":
        pass
    if infoText=="Déclaration déposée - publication en préfecture à venir":
        pass
    if infoText =="Déclaration non déposée":
        pass
    if infoText =="En cours":
        pass
    pass

def get_list_url(section):
    links = section.find_all("a",class_="dl-declaration-history")
    listurl = []
    for link in links:
        if link.text=="Version XML":
            listurl.append(link["href"])
    return listurl



def create_declare(hopol_id,typedecla,dateTraitement,status,mongoId):
    declaration = DeclarationMoney()
    declaration.hopol_id=hopol_id
    declaration.type_declaration = typedecla
    declaration.status = status
    declaration.id_mongo=mongoId
    declaration.date_traitement = dateTraitement
    return declaration



def create_mongo(link,mongoCollection,typedecla):
    data = jsondata_from_xml(link)
    data = data["declaration"]
    data["_id"] = data["uuid"]
    data["type_declaration"]=typedecla
    data.pop("uuid")
    mongoCollection.update_one(
                    {"_id": data["_id"]},  # cherche l'id et l'upsert 
                    {"$set": data},
                    upsert=True                  
                )
    return data["_id"]

if __name__=="__main__":
    proccess_all()