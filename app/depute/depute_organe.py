import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from db.mongoDB import mongoConnection
from db.postgreSQL import HommePolitique , Organe,OrganeRelation 
from utils.date_utils import get_date
from utils.db_import import import_gen , get_count_doc_left , import_gen_single
import logging
logger = logging.getLogger(__name__)

dbName = os.getenv("MONGO_DBNAME")

def start_import_hopol():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "acteur" in collection_list:
            collection = database["acteur"]

            hopol_total = get_count_doc_left(collection,"insertion_traite")
            import_gen(collection,HommePolitique,"insertion_traite",["hopol_id"],create_hopol,nomComplet="Insertion des députes",total=hopol_total)
            hopol_total_bug = get_count_doc_left(collection,"insertion_traite")
            import_gen(collection,HommePolitique,"insertion_traite",["hopol_id"],create_hopol,nomComplet="Insertion des députes de maniere individuel",total=hopol_total_bug,chunckSize=1)#Fait l'insertion avec le plus petit chunk pour s'assurer d'avoir traiter tout ce qui est possible de traité
            print("Insertion des députés faites")

            hopolrel_total = get_count_doc_left(collection,"relation_organe")#Pour l'instant liste uniquement les documents et pas les mandats individuel
            import_gen(collection,OrganeRelation,"relation_organe",["organe_id","hopol_id","qualite","date_debut"],create_link_organe,nomComplet="Insertion des mandats",total=hopolrel_total,chunckSize=1)
            hopolrel_total_bug = get_count_doc_left(collection,"relation_organe")#Pour l'instant liste uniquement les documents et pas les mandats individuel
            import_gen_single(collection,"relation_organe",create_link_organe,total=hopolrel_total_bug,nomComplet="Insertion des mandats de maniere individuel")
            print("Insertion des mandats de députés fait")
            return hopol_total+hopolrel_total
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import pas de table acteur : {collection_list}")
            return 0#A completer

def start_insert_organe():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "organe" in collection_list:
            collection = database["organe"]
            organe_total = get_count_doc_left(collection,"insertion_traite")
            import_gen(collection,Organe,"insertion_traite",["organe_id"],create_organe,nomComplet="Insertion des organes parlementaire",total=organe_total)
            print("Insertion des organes parlementaire faites")
            return organe_total
        else:
            print(f"Erreur dans le traitement de la base de donnée d'import pas de table organe : {collection_list}")
            return 0#A completer

        
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

def full_import():
    total =0
    total+=start_insert_organe()
    total+=start_import_hopol() 
    return total

if __name__=="__main__":
    full_import()