from db.mongoDB import mongoConnection
from db.postgreSQL import Vote,VoteRelation
from utils.date_utils import get_date
from utils.db_import import import_gen , get_count_doc_left ,import_gen_single
import os

import logging
logger = logging.getLogger(__name__)

dbName = os.getenv("MONGO_DBNAME")
def start_import_vote():
    with mongoConnection.get_connection() as client:
        database = client[dbName]
        collection_list = database.list_collection_names()
        if "scrutin" in collection_list:
            collection = database["scrutin"]
            #On insert les votes dans leur table
            vote_total = get_count_doc_left(collection,"insertion_traite")
            import_gen(collection,Vote,"insertion_traite",["vote_id"],create_vote,total=vote_total,nomcomplet="Insertion en chunks des votes")
            vote_remaining = get_count_doc_left(collection,"insertion_traite")
            #On recommence l'operation mais cette fois avec des chunk plus petit pour s'assurer que si il y a une erreur elle est de taille minimal
            import_gen(collection,Vote,"insertion_traite",["vote_id"],create_vote,total=vote_remaining,chunckSize=1,nomComplet="Insertion vote par vote")

            #On va generer les position de chacun. Doit faire un refacto de import_gen pour tracker correctement les process interne si on veut faire une estimation plus precise.
            #On fait l'import en trois étapes qui sont de plus en plus précis pour s'assurer que les entrés non traité sont les plus petite possible
            vote_nominatif_total = get_count_doc_left(collection,"creation_vote_nominatif")
            import_gen(collection,VoteRelation,"creation_vote_nominatif",["hopol_id","vote_id"],create_vote_indiv,total=vote_nominatif_total,nomComplet="Insertion en chunks des position de vote")
            vote_nominatif_restant= get_count_doc_left(collection,"creation_vote_nominatif")
            import_gen(collection,VoteRelation,"creation_vote_nominatif",["hopol_id","vote_id"],create_vote_indiv,total=vote_nominatif_restant,chunckSize=1,nomComplet="Insertion document par document des position de vote")
            vote_nominatif_restant=get_count_doc_left(collection,"creation_vote_nominatif")
            import_gen_single(collection,"creation_vote_nominatif",create_vote_indiv,vote_nominatif_restant,"Import final des votes individuels")
            return vote_total+vote_nominatif_total

        else:
            print(f"Erreur dans le traitement de la base de donnée d'import pas de table scrutin : {collection_list}")
            return 0 #A completer

def get_total_vote(collection):
    return collection.count_documents({})

#Fonction d'aggregation qui compte le nombre de vote total
def get_total_indiv_vote(collection):
    retour = collection.aggregate([
    {
        '$group': {
            '_id': 'expression', 
            'somm_votes': {
                '$sum': {
                    '$toInt': '$syntheseVote.nombreVotants'
                }
            }
        }
    }
    ])
    retour = list(retour) 
    if len(retour)==1:
        return retour[0]["somm_votes"]
    
#Fonction pour creer le vote en lui meme
def create_vote(vote_mongo,listajout):
    vote = Vote()
    vote.vote_id=vote_mongo["_id"]
    vote.organe_votant=vote_mongo["organeRef"]
    vote.nom = vote_mongo["titre"]
    vote.date=get_date(vote_mongo["dateScrutin"])
    vote.organe_votant=vote_mongo["organeRef"]
    synthese = vote_mongo["syntheseVote"]
    vote.nombre_votant = synthese["nombreVotants"]
    vote.suffrage_exprime=synthese["suffragesExprimes"]
    vote.resultat = format_resultat(synthese["annonce"])
    listajout.append(vote)

def format_resultat(annonce):
    if annonce =="l'Assemblée nationale a adopté":
        return "Adopté"
    if annonce =="L'Assemblée nationale n'a pas adopté":
        return "Non-Adopté"
    #TODO Lever erreur
    return "Erreur"

def create_vote_indiv(vote,listajout):
    vote_id = vote["_id"]
    list_organe = vote["ventilationVotes"]["organe"]["groupes"]["groupe"]
    for organe in list_organe:
        organe_id=organe["organeRef"]
        listvotant=organe["vote"]["decompteNominatif"]
        #On fait les 4 categories de votes et on les formats pour que ce soit la liste des votants
        pour = format_positions(listvotant["pours"])
        contre =  format_positions(listvotant["contres"])
        non_votant = format_positions(listvotant["nonVotants"])
        abstention =  format_positions(listvotant["abstentions"])

        for votant in pour:
            listajout.append(create_vote_indiv_categorie(votant,"pour",organe_id,vote_id))
        for votant in contre:
            listajout.append(create_vote_indiv_categorie(votant,"contre",organe_id,vote_id))
        for votant in non_votant:
            listajout.append(create_vote_indiv_categorie(votant,"non_votant",organe_id,vote_id))
        for votant in abstention:
            listajout.append(create_vote_indiv_categorie(votant,"abstention",organe_id,vote_id))
                   
def create_vote_indiv_categorie(votant,typeVote,groupeParId,vote_id):
    relation = VoteRelation()
    relation.groupe_parlementaire=groupeParId
    relation.hopol_id=votant["acteurRef"]
    relation.vote_id=vote_id
    relation.position=typeVote
    return relation

def format_positions(positionliste):
    #Si il n'y a personne le field englobant est null
    if positionliste == None:
        return []
    votants = positionliste["votant"]
    if votants!=None:
        if isinstance(votants,list):
            return votants
        else:
            #Si il n'y a qu'un votant le field votant n'est pas une liste mais directement la personne qui a voté
            return [votants]
    else:
        print(f"Erreur sur {positionliste}")
