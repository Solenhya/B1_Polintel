import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from db.postgreSQL.utils import upsert_orm
from db.postgreSQL import HommePolitique , PartiPolitique , Organe,OrganeRelation
from tqdm import tqdm
from datetime import datetime
from pymongo import UpdateOne
from utils.date_utils import get_date

dbName = os.getenv("DBNAME_DEPUTE_IMPORT")

def start_import():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collections()
        hopol = None
        organe = None

def start_import_hopol():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "acteur" in collection_list:
            collection = database["acteur"]
            
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import par de table acteur : {collection_list}")
            return #A completer

def import_hopol(collection):
    batch_done=[]
    query = {"insertion_traite":{"$exists":False}}
    checkpointQuant = 10
    current = 0

    for hopol in tqdm(collection.find(query)):
        insert_hopol(hopol)
        currentDate = datetime.now()
        batch_done.append(UpdateOne(
        {"_id": hopol["_id"]},
        {"$set": {"done": {"date":currentDate}}}))
        if(len(batch_done)>checkpointQuant):
            collection.bulk_write(batch_done)
            print(f"Checkpoint effectuer au {current}")
        current+=1


def insert_hopol(hopol):
    ajout = HommePolitique()
    ajout.hopol_id = hopol["_id"]
    #A poser la question gestion d'erreur comment le gerer
    ident = hopol["etatCivil"]["ident"]
    ajout.nom = ident["nom"]
    ajout.prenom = ident["prenom"]

    naissance = hopol["etatCivil"]["infoNaissance"]
    ajout.date_naissance = get_date(naissance["dateNais"])
    ajout.role_actuel="depute"
    
    ajout.profession_cat=hopol["profession"]["socProcINSEE"]["catSocPro"]
    ajout.profession=hopol["profession"]["libelleCourant"]
    
    #TODO link avec les organisation , les parties politique ect

def start_insert_organe():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "organe" in collection_list:
            collection = database["organe"]
            insert_organes(collection)
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import par de table organe : {collection_list}")
            return #A completer

def insert_organes(collection):
    """Une fois qu'on a la collection des organes on va extraire les parties politique et l'assemblee"""
    batch_done=[]
    nameOperation = "insertion_traite"
    query = {nameOperation:{"$exists":False}}
    #La taille des checkpoints
    checkpointQuant = 20
    current = 1
    #Les deux liste d'objet possible : Partie politique ou autre
    parpolAjout=[]
    otherAjout=[]

    #on se connecte a la base de donnée
    with db_connection.get_session() as session:
        for data in tqdm(collection.find(query)):
            #La fonction ajoute les objets dans les bonnes listes
            create_organe(data,parpolAjout,otherAjout)
            currentDate = datetime.now()
            #On creer l'update qui indique qu'on a traité l'information
            batch_done.append(UpdateOne(
            {"_id": data["_id"]},
            {"$set": {nameOperation: {"date":currentDate}}}))

            #Si on a atteint la taille de batch on écrit dans les deux db
            if(len(batch_done)>checkpointQuant):
                upsert_orm(session,PartiPolitique,parpolAjout,["id"])
                upsert_orm(session,Organe,otherAjout,["organe_id"])
                collection.bulk_write(batch_done)
                parpolAjout=[]
                otherAjout=[]
                batch_done=[]
                tqdm.write(f"Checkpoint effectuer a la {current} operation")
            current+=1

def create_organe(organeinfo,listParpol,listother):
    codetype=organeinfo["codeType"]
    if(codetype=="ASSEMBLEE"):#Il s'agit de l'organe qui represente l'assemblé et est donc pas traité
        pass
    elif(codetype=="PARPOL"):#Le partie politique il est traité differement
        organe = PartiPolitique()
        organe.date_creation = get_date(organeinfo["viMoDe"]["dateDebut"])
        organe.nom = organeinfo["libelle"]
        organe.id = organeinfo["_id"]
        listParpol.append(organe)
    else:
        organe = Organe()
        organe.organe_id=organeinfo["_id"]
        organe.code_type = organeinfo["codeType"]
        organe.type = organeinfo["type"]
        organe.nom = organeinfo["libelle"]
        organe.debut = organeinfo["viMoDe"]["dateDebut"]
        organe.fin = organeinfo["viMoDe"]["dateFin"]
        listother.append(organe)
    
if __name__=="__main__":
    start_insert_organe()