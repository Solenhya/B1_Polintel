from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Date
from .database import Base

#La définition des table postgre via sqlalchemy models
class HommePolitique(Base):
    __tablename__ = "hommepolitique"
    hopol_id = Column(String, primary_key=True)
    role_actuel=Column(String)#Est ce que c'est un député ou un senateur
    prenom=Column(String)
    nom=Column(String)
    date_naissance = Column(Date)
    proffession=Column(String)

class Organe(Base):
    __tablename__ = "organe"
    organe_id=Column(String,primary_key=True)
    nom=Column(String)
    type=Column(String)
    code_type = Column(String)
    debut=Column(Date)
    fin=Column(Date)

class Activite(Base):
    __tablename__="activite"
    activite_id=Column(String,primary_key=True)

