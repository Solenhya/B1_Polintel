import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
import re
from db.mongoDB import mongoConnection
from db.postgreSQL import db_connection
from sqlalchemy import select
from db.postgreSQL.models import OrganeRelation , Organe , Election
from dotenv import load_dotenv
load_dotenv()
dbName = os.getenv("MONGO_DBNAME")
import requests
import logging
logger = logging.getLogger(__name__)
from tqdm import tqdm

rid="5163f2e3-1362-4c35-89a0-1934bb74f2d9"
baseurl="https://tabular-api.data.gouv.fr/api/resources/"
parametercirc="Code circonscription législative__exact"

def get_election(codedepartement,codecirconscription):
    codecirconscriptionclean=codecirconscription
    if(type(codecirconscription)!=str):
        codecirconscriptionclean=str(codecirconscription)
    taillecircons = len(codecirconscriptionclean)
    if(taillecircons>2):
        print(f"Erreur dans la ciconscription : {codecirconscriptionclean}")
        #Bug trop long
        return
    if(taillecircons<1):
        print(f"Erreur dans la ciconscription : {codecirconscriptionclean}")
        #Bug trop court
        return
    if(taillecircons==1):
        #Il manque le 0 devant
        codecirconscriptionclean="0"+codecirconscriptionclean
    #Fait le cleaning du departement
    codedepartement=format_departement(codedepartement)
    codecomplet=codedepartement+codecirconscriptionclean
    url=baseurl+rid+"/data/"
    parameters = {parametercirc:codecomplet}
    requete = requests.get(url,params=parameters)

    if(requete.status_code==200):
        retour = requete.json()
        retour["origine"]=codecomplet
        return retour
    else:
        logger.error(f"Erreur dans la requete mauvais status code : {requete.status_code}")
        print(f"Erreur dans la requete mauvais status code : {requete.status_code}")
        #Bug sur la connection
        return None

def format_departement(departement):
    if(departement=="099"):
        #Dans le cas des Francais a l'étranger la désignation n'est pas la meme sur l'api
        return "ZZ"
    if(departement=="977"):
        #Saint bartelemy /Saint martin qui est fait autrement
        return "ZX"
    return departement.lstrip("0")

def get_formated(retour):
    if(retour==None or retour["origine"]==None):
        logger.error(f"Erreur lors de la récuperation de l'éléction via API on a recu : {retour}")
        return
    if(retour["data"]==None or type(retour["data"])!=list):
        logger.error(f"Erreur dans la recuperation de l'election via API sur le format de la requete:{retour} quand on requete {retour["origine"]}")
        return
    if(len(retour["data"])==0 or retour["data"][0]==None):
        logger.error(f"Erreur dans la recuperation de l'election via API le retour n'a pas d'élément 0 {retour["data"]} quand on requete {retour["origine"]}. La requete : {retour}")
        return
    return retour["data"][0]

def process_elections():
    count = 0
    with db_connection.get_session() as session:
        with mongoConnection.get_connection() as client:
            collectionBase = client[dbName]["organe"]
            collectionFinal=client[dbName]["election"]
            toProcess = select(Election,Organe).join(Election.poste).where((Election.gagnant_voix.is_(None)))#On se base sur l'election n'a pas le nombre de voix du gagnant
            results = session.execute(toProcess).all() 
            for row in tqdm(results):
                #TODO try and logg
                election , organe = row
                code = election.organe_id
                mongodata = collectionBase.find_one({"_id":code})
                codeCirconscription = mongodata["numero"]
                codeDepart = mongodata["lieu"]["departement"]["code"]
                infoelec = get_formated(get_election(codeDepart,codeCirconscription))
                if infoelec==None:
                    print(f"Erreur sur : {election.organe_id} nom {organe.nom}")
                    continue
                infoelec = create_elec_obj(infoelec)
                liste_candidat = infoelec["candidats"]
                liste_candidat = sort_candidat(liste_candidat)#Recupere la liste des candidats et la trie en fonction des Voix obtenu
                addto_election(election,liste_candidat,infoelec)
                session.commit()
                collectionFinal.update_one({"_id":infoelec["_id"]},{"$set":infoelec})
                count+=1
    return count

def create_elec_obj(elecInfo):
    pattern_full = re.compile(r'\s\d+$')          # Pattern de test de champs candidat
    pattern_capture = re.compile(r'^(.*)\s(\d+)$') # capturer la clef et le numero de candidat
    retour = {}
    #On creer un dictionaire pour les candidats pour y ranger toute les info avant de le retransformer en liste
    retour["candidats"]={}
    candidat=retour["candidats"]
    for key,value in elecInfo.items():
        if pattern_full.search(key):
            #Si on est dans le cas ou c'est un champs de candidats
            prefix = pattern_capture.match(key).group(1)
            number = pattern_capture.match(key).group(2)
            if(value!=None):
                if number not in candidat:
                        candidat[number] = {}
                candidat[number][prefix]=value
        else:
            retour[key]=value
    #On collapse les indices en liste une fois qu'on a recuperer toutes les infos qui y font reference
    retour["candidats"]=debrut_candidats(retour["candidats"])
    retour["_id"]=retour["__id"]#Parce que deux _ c'est trop pour mongo
    retour.pop("__id")
    return retour

def debrut_candidats(candidats):
    return list(candidats.values())

def sort_candidat(resulats):
    sorted_result = sorted(resulats,key=lambda x:x["Voix"],reverse=True)#Sorted trie la liste en prenant l'élement "Voix" du dictionnaire au lieu de l'élément
    return sorted_result

def addto_election(election:Election,sorted_list_candidats,election_data):
    election.gagnant_voix=sorted_list_candidats[0]["Voix"]
    runnerup = sorted_list_candidats[1]
    election.runnerup_voix=runnerup["Voix"]
    circons = election_data["Libellé circonscription législative"]
    departement = election_data["Libellé département"]
    election.nom_complet = f"{circons} {departement}"
    first_name = runnerup.get("Prénom candidat","")#Recupere le prénom ou vide si il n'existe pas
    last_name = runnerup.get("Nom candidat","")
    nom_complet = f"{first_name.capitalize()} {last_name.capitalize()}".strip()
    election.runnerup_name=nom_complet
    election.nbr_inscrit=election_data["Inscrits"]
    election.nbr_votant=election_data["Votants"]
    election.nbr_blancs=election_data["Blancs"]

if __name__=="__main__":
    process_elections()