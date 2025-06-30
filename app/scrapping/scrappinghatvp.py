import requests
from bs4 import BeautifulSoup
from utils.json_import import jsondata_from_xml
from db.mongoDB import mongoConnection
import os
dbName = os.getenv("MONGO_DBNAME") 

import logging
logger = logging.getLogger(__name__)

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
