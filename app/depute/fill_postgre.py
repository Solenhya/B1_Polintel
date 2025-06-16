import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from db.postgreSQL.utils import upsert_orm ,upsert
from db.postgreSQL import HommePolitique , Organe,OrganeRelation , Activite
from tqdm import tqdm
from datetime import datetime
from pymongo import UpdateOne
from utils.date_utils import get_date
import logging
from depute.recuperation_election import process_elections
logger = logging.getLogger(__name__)

dbName = os.getenv("MONGO_DBNAME")

def start_import_hopol():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "acteur" in collection_list:
            collection = database["acteur"]
            import_gen(collection,HommePolitique,"insertion_traite",["hopol_id"],create_hopol)
            import_gen(collection,OrganeRelation,"relation_organe",["organe_id","hopol_id","qualite","date_debut"],create_link_organe)
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import par de table acteur : {collection_list}")
            return #A completer

def start_insert_organe():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "organe" in collection_list:
            collection = database["organe"]
            #insert_organes(collection)
            import_gen(collection,Organe,"insertion_traite",["organe_id"],create_organe)
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import par de table organe : {collection_list}")
            return #A completer

def import_gen(collection,model,nameOperation,conflictCol,objCreation):
    """Une fonction generique pour l'insertion en bulk d'une collection mongodb vers une db postgreSQL"""
    batch_done=[]
    query = {f"_traitement.{nameOperation}":{"$exists":False}}
    #La taille des checkpoints
    checkpointQuant = 20
    current = 1
    #Les deux liste d'objet possible : Partie politique ou autre
    objAjout=[]
    #on se connecte a la base de donnée
    with db_connection.get_session() as session:
        for data in tqdm(collection.find(query)):
            #La fonction ajoute les objets dans les bonnes listes
            objCreation(data,objAjout)
            currentDate = datetime.now()
            #On creer l'update qui indique qu'on a traité l'information
            batch_done.append(UpdateOne(
            {"_id": data["_id"]},
            {"$set": {f"_traitement.{nameOperation}": {"date":currentDate}}}))

            #Si on a atteint la taille de batch on écrit dans les deux db
            if(len(batch_done)>checkpointQuant):
                do_insert(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session)
            current+=1
        if(len(batch_done)>0):
            do_insert(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session)

def do_insert(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session):
    upsert_orm(session,model,objAjout,conflictCol)
    collection.bulk_write(batch_done)
    objAjout.clear()
    batch_done.clear()
    tqdm.write(f"Checkpoint effectuer pour {model.__name__} pour {nameOperation} a la {current} operation")
        
def create_organe(organeinfo,listajout):
    organe = Organe()
    organe.organe_id=organeinfo["_id"]
    organe.code_type = organeinfo["codeType"]
    organe.type = organeinfo["type"]
    organe.nom = organeinfo["libelle"]
    organe.debut = get_date(organeinfo["viMoDe"]["dateDebut"])
    organe.fin = get_date(organeinfo["viMoDe"]["dateFin"])
    listajout.append(organe)

def create_hopol(hopol,listajout):
    ajout = HommePolitique()
    ajout.hopol_id = hopol["_id"]
    ident = hopol["etatCivil"]["ident"]
    ajout.nom = ident["nom"]
    ajout.prenom = ident["prenom"]
    naissance = hopol["etatCivil"]["infoNaissance"]
    ajout.date_naissance = get_date(naissance["dateNais"])
    ajout.profession_cat=hopol["profession"]["socProcINSEE"]["catSocPro"]
    ajout.profession=hopol["profession"]["libelleCourant"]
    listajout.append(ajout)

def create_link_organe(hopol,listajout):
    listeMandat = hopol["mandats"]["mandat"]
    for mandat in listeMandat:
        relation = OrganeRelation()
        relation.hopol_id=hopol["_id"]
        if relation.hopol_id==None:
            print(f"Erreur sur la creation de {mandat} id hopol est vide: {hopol["_id"]}")
            return
        relation.organe_id=mandat["organes"]["organeRef"]
        if relation.organe_id==None:
            print(f"Erreur sur la creation de {mandat} id organe est vide")
            return
        relation.date_debut=get_date(mandat["dateDebut"])
        if relation.date_debut==None:
            print(f"Erreur sur la creation de {mandat} erreur sur la date de début est vide")
            return
        if mandat["dateFin"]!=None:
            relation.date_fin=get_date(mandat["dateFin"])
        relation.qualite = mandat["infosQualite"]["codeQualite"]
        if mandat["infosQualite"]["codeQualite"]==None:
            print(f"Erreur : {relation.hopol_id} avec {relation.organe_id}")
            relation.qualite="Inconnue"
        listajout.append(relation)
        code = mandat["typeOrgane"]
        if code =="ASSEMBLEE":
            circons = OrganeRelation()
            circons.hopol_id=hopol["_id"]
            circons.date_debut=get_date(mandat["dateDebut"])
            if mandat["dateFin"]!=None:
                circons.date_fin=get_date(mandat["dateFin"])
            election = mandat["election"]
            circons.organe_id=election["refCirconscription"]
            circons.qualite="élu"
            listajout.append(circons)

def create_activite_vote(vote,listajout):
    activite = Activite()
    activite.activite_id=vote["_id"]
    activite.type="vote"
    activite.nom = vote["titre"]
    activite.date=get_date(vote["dateScrutin"])
    listajout.append(activite)

def create_activite_link(vote,listajout):
    list_organe = vote["ventilationVotes"]["organe"]["groupes"]["groupe"]
    for organe in list_organe:
        listvotant=organe["vote"]["decompteNominatif"]

#Fonction pour reset entierement le traitement sur une collection en particulier
def clear_procces_full(dbName,collectionName):
    with mongoConnection.get_connection() as client:
        collection=client[dbName][collectionName]
        query={"$unset":{"_traitement":""}}
        collection.update_many({},query)

#Fonction qui liste toute les collections a reset
def clear_all_process(dbName):
    clear_procces_full(dbName,"acteur")
    clear_procces_full(dbName,"organe")
    clear_procces_full(dbName,"vote")


if __name__=="__main__":
    start_insert_organe()
    start_import_hopol()
    process_elections()