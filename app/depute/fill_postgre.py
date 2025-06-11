import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from db.postgreSQL.models import HommePolitique
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
            
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import par de table organe : {collection_list}")
            return #A completer

def insert_organes(collection):
    batch_done=[]
    nameOperation = "insertion_traite"
    query = {nameOperation:{"$exists":False}}
    checkpointQuant = 10
    current = 1
    for organe in tqdm(collection.find(query)):
        insert_hopol(organe)
        currentDate = datetime.now()
        batch_done.append(UpdateOne(
        {"_id": organe["_id"]},
        {"$set": {nameOperation: {"date":currentDate}}}))
        if(len(batch_done)>checkpointQuant):
            collection.bulk_write(batch_done)
            tqdm.write(f"Checkpoint effectuer a la {current} operation")
        current+=1

def insert_organe(organe):
    pass