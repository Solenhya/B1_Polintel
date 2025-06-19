from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from tqdm import tqdm
from datetime import datetime
from pymongo import UpdateOne
from db.postgreSQL.utils import upsert_orm
import logging
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)

# Create file handler
file_handler = logging.FileHandler('import.log')
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(file_handler)


def import_gen(collection,model,nameOperation,conflictCol,objCreation,total=None,nomComplet="Import",chunckSize=20):
    """Une fonction generique pour l'insertion en bulk d'une collection mongodb vers une db postgreSQL
    Elle fonctionne sur une liste de document (de taille chunkSize a chaque fois) et si elle fonctionne elle déclare le traitement réaliser pour le chunk. Si elle ne réussi pas elle ne déclare rien et l'on peut y revenir de maniere plus précise    
    """
    batch_done=[]
    query = {f"_traitement.{nameOperation}":{"$exists":0}}
    #La taille des checkpoints
    checkpointQuant = chunckSize
    current = 1
    #Les deux liste d'objet possible : Partie politique ou autre
    objAjout=[]
    #on se connecte a la base de donnée
    with db_connection.get_session() as session:
        for data in tqdm(collection.find(query),total=total,desc=nomComplet):
            #La fonction ajoute les objets dans les bonnes listes
            objCreation(data,objAjout)
            currentDate = datetime.now()
            #On creer l'update qui indique qu'on a traité l'information
            batch_done.append(UpdateOne(
            {"_id": data["_id"]},
            {"$set": {f"_traitement.{nameOperation}": {"date":currentDate,"status":"Success"}}}))

            #Si on a atteint la taille de batch on écrit dans les deux db
            if(len(batch_done)>checkpointQuant):
                do_insert_bulk(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session)
            current+=1
        if(len(batch_done)>0):
            do_insert_bulk(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session)

def do_insert_bulk(collection, model, nameOperation, conflictCol, batch_done, current, objAjout, session):
    try:
        upsert_orm(session,model,objAjout,conflictCol)
        collection.bulk_write(batch_done)
        objAjout.clear()
        batch_done.clear()
        tqdm.write(f"Checkpoint effectuer pour {model.__name__} pour {nameOperation} a la {current} operation")
    except SQLAlchemyError as sqle:
        tqdm.write(f"Erreur SQL dans l'insertion d'un chunks de donnée:{batch_done}.Plus de detail dans le log")
        logger.error(msg=f"Erreur SQL insertion. Erreur: {sqle.orig} sur {sqle.params}")
        objAjout.clear()
        batch_done.clear()
        session.rollback()
    except Exception as e:
        tqdm.write(f"Erreur dans l'insertion d'un chunks de donnée : {batch_done}. Plus de detail dans le log")
        logger.error(msg=f"Erreur dans l'insertion d'un chunks de donnée : {batch_done}. Erreur : {e}")
        objAjout.clear()
        batch_done.clear()
        session.rollback()

def import_gen_single(collection,nameOperation,objCreation,total=None,nomComplet="Import unitaire"):
    query = {f"_traitement.{nameOperation}":{"$exists":0}}
    objAjout=[]
    with db_connection.get_session() as session:
        for data in tqdm(collection.find(query),total=total,desc=nomComplet):
            objCreation(data,objAjout)
            currentDate = datetime.now()
            dataId = data["_id"]
            insert_single(collection,nameOperation,currentDate,dataId,objAjout,session)

def insert_single(collection,nameOperation,currentDate,dataId,listAjout,session):
    """Une fonction qui va travailler sur une liste d'object creer depuis un seul document mongo qui peut avoir des conflict dans cette liste. Elle permets de continuer le traitement sur cette liste malgré les conflictS. Elle va écrire le nombre d'erreur"""
    nombreErreur = 0
    nombreOperation = len(listAjout)
    for ajout in listAjout:
        try:
            session.add(ajout)
            session.commit()
        except Exception as e:
            logger.error(f"Erreur dans l'import de donnée {nameOperation} par objet sur {dataId} . Erreur : {e}")
            nombreErreur+=1
            session.rollback()
    queryName = f"_traitement.{nameOperation}"
    if(nombreErreur==0):
        status="Success"
    elif(nombreErreur==nombreOperation):
        status="Error"
    else:
        status="Partial"
        
    data = {"date":currentDate,"status":status,"nombreErreur":nombreErreur}
    collection.update_one(
    {"_id": dataId},
    {"$set": {queryName: data}}
    )
    listAjout.clear()
    

def get_count_doc_left(collection,operation_name):
    query = {f"_traitement.{operation_name}":{"$exists":0}}
    count = collection.count_documents(query)
    return count

