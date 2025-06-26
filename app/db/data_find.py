from db.postgreSQL import db_connection
from db.postgreSQL.models import HommePolitique , Vote , Organe
from db.mongoDB import mongoConnection
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import and_
from pydantic import BaseModel , Field
from typing import Any, Optional, Dict, List
import os
dbName = os.getenv("MONGO_DBNAME")
from exceptions.customExceptions import IncorrectInputException
from enum import Enum

def get_dynamic_query(conditions,orm_model,session):
    if conditions:
        if len(conditions)==1:
            #and_ a besoin de deux element minimum donc on doit gerer le cas = 1
            query = session.query(orm_model).filter(conditions[0])
        else:
            query = session.query(orm_model).filter(and_(*conditions))
            #L'expression *conditions unpack la liste pour etre passer a and_ qui creer la requete SQL
    else:
        query = session.query(orm_model)
    results = query.all()
    return results
class BaseHopolRequest(BaseModel):
    #Les categorie precise de la table
    hopol_ids : Optional[List[str]] = Field(None,description="")
    prenom : Optional[str] = Field(None,description="")
    nom : Optional[str] = Field(None,description="")
    proffession : Optional[str] = Field(None,description="")
    cat_proffes : Optional[str] = Field(None,description="")
    birth_year : Optional[int]=Field(None,description="")

    #Les categories plus flexible
    searchTerm : Optional[str]=Field(None,description="Un terme de recheche pour le prenom nom. Exemple si 'Pa' On trouve pascal taffet , patrick wampé et sophie Panonacle. NOT_FUNCTIONNAL") #Un terme de recheche pour le prenom nom. Exemple si "Pa" On trouve pascal taffet , patrick wampé et sophie Panonacle
    age_min:Optional[int]=Field(None,description="NOT_FUNCTIONNAL")
    age_max:Optional[int]=Field(None,description="NOT_FUNCTIONNAL")


def get_hopols(requete : BaseHopolRequest):
    with db_connection.get_session() as session:
        #Creer un liste des filtres potentiel
        conditions = []
        if(requete.hopol_ids):
            conditions.append(HommePolitique.hopol_id.in_(requete.hopol_ids))
        if requete.prenom:
            conditions.append(HommePolitique.prenom==requete.prenom)
        if requete.nom:
            conditions.append(HommePolitique.nom==requete.nom)
        if(requete.proffession):
            conditions.append(HommePolitique.profession==requete.proffession)
        if requete.cat_proffes:
            conditions.append(HommePolitique.profession_cat==requete.cat_proffes)
        if requete.birth_year:
            conditions.append(HommePolitique.date_naissance.year==requete.birth_year)

        results = get_dynamic_query(conditions,HommePolitique,session)
        retour = []
        for result in results:
            dictio = result.__dict__.copy()
            dictio.pop("_sa_instance_state")
            retour.append(dictio)
    return retour


def get_name_collection(type_doc):
    if(type_doc=="homme-politique"):
        return "acteur"
    if(type_doc=="organe"):
        return "organe"
    if(type_doc=="vote"):
        return "scrutin"
    if(type_doc=="election"):
        return "election"
    if(type_doc=="declaration-monetaire"):
        return "declaration_money"

def get_mongo_document(type_doc,id_doc):
    if not isinstance(id_doc,str):
        raise IncorrectInputException("Acces mongo document",f"Erreur dans l'input utilisateur l'id doit etre un string : {id_doc} est un {type(id_doc)}")
    type_format = get_name_collection(type_doc)
    if(type_format==None):
        raise IncorrectInputException("Access mongo document",f"Erreur dans l'acces a la collection. {type_doc} n'est pas une collection reconnue")
    with mongoConnection.get_connection() as client:
        collection = client[dbName][type_format]
        document = collection.find_one({"_id":id_doc})
        return document
    
class BaseVoteRequete(BaseModel):
    vote_ids : Optional[List[str]] = Field(None,description="")
    adopte : Optional[bool] = Field(None,description="")
    nom : Optional[str] = Field(None,description="")
    votantMin : Optional[int] = Field(None,description="")
    votantMax : Optional[int] = Field(None,description="")
    vote_year : Optional[int]=Field(None,description="")

def get_votes(requete : BaseVoteRequete):
    conditions = []
    if(requete.hopol_ids):
        conditions.append(Vote.vote_id.in_(requete.vote_ids))
    if requete.nom:
        conditions.append(Vote.nom==requete.nom)
    if requete.vote_year:
        conditions.append(Vote.date.year==requete.vote_year)
    
    if(requete.votantMin is not None and requete.votantMax is not None and requete.votantMin>requete.votantMax):
        raise IncorrectInputException("Access vote list",message=f"Erreur dans le nombre de vote requis min>max:{requete.votantMin}>{requete.votantMax}")
    
    if(requete.votantMin is not None):
        conditions.append(Vote.nombre_votant>=requete.votantMin)
    if(requete.votantMax is not None):
        conditions.append(Vote.nombre_votant<=requete.votantMax)

    with db_connection.get_session() as session:
        resultas = get_dynamic_query(conditions,Vote,session)
        retour = []
        for result in resultas:
            dictio = result.__dict__.copy()
            dictio.pop("_sa_instance_state")
            retour.append(dictio)
        return retour

class OrganeType(Enum):
    #TODO
    """On peut definir les type possible pour les exposer en enum dans la requete"""
    pass

class BaseOrganeRequete(BaseModel):
    organe_ids : Optional[List[str]] = Field(None,description="")
    actif : Optional[bool] = Field(None,description="Est ce que l'organe est actif.(Est ce qu'il a une date de fin)")
    nom : Optional[str] = Field(None,description="")
    year_debut_Min : Optional[int] = Field(None,description="")
    year_debut_Max : Optional[int] = Field(None,description="")
    year_debut : Optional[int]=Field(None,description="L'année exacte du début ")
    code_type : Optional[str]=Field(None,description=f"Le code type de l'organe. Par exemple : 'CIRCONSCRIPTION' ou 'ORGEXTPARL'")

def get_organes(requete:BaseOrganeRequete):
    conditions = []
    if(requete.organe_ids):
        conditions.append(Organe.vote_id.in_(requete.vote_ids))
    if(requete.actif):
        conditions.append(Organe.fin is None)
    if requete.nom:
        conditions.append(Organe.nom==requete.nom)
    if requete.year_debut:
        conditions.append(Organe.debut.year==requete.year_debut)
    
    if(requete.year_debut_Min is not None and requete.year_debut_Max is not None and requete.year_debut_Min>requete.year_debut_Max):
        raise IncorrectInputException("Access vote list",message=f"Erreur dans le nombre de vote requis min>max:{requete.year_debut_Min}>{requete.year_debut_Max}")
    
    if(requete.year_debut_Min is not None):
        conditions.append(Organe.debut.year>=requete.year_debut_Min)
    if(requete.year_debut_Max is not None):
        conditions.append(Organe.debut.year<=requete.year_debut_Max)
    with db_connection.get_session() as session:
        resultas = get_dynamic_query(conditions,Organe,session)
        retour = []
        for result in resultas:
            dictio = result.__dict__.copy()
            dictio.pop("_sa_instance_state")
            retour.append(dictio)
        return retour

def get_hopol_info(requete : BaseHopolRequest):
    with db_connection.get_session() as session:
        #Creer un liste des filtres potentiel
        conditions = []
        if(requete.hopol_ids):
            conditions.append(HommePolitique.hopol_id.in_(requete.hopol_ids))
        if requete.prenom:
            conditions.append(HommePolitique.prenom==requete.prenom)
        if requete.nom:
            conditions.append(HommePolitique.nom==requete.nom)
        if(requete.proffession):
            conditions.append(HommePolitique.profession==requete.proffession)
        if requete.cat_proffes:
            conditions.append(HommePolitique.profession_cat==requete.cat_proffes)
        if requete.birth_year:
            conditions.append(HommePolitique.date_naissance.year==requete.birth_year)

        results = get_dynamic_query(conditions,HommePolitique,session)
        retour = []
        for result in results:
            dictio = result.to_dict()
            retour.append(dictio)
    return retour