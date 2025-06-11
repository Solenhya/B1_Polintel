from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Date
from sqlalchemy.orm import relationship
from .database import Base

#La définition des table postgre via sqlalchemy models
class HommePolitique(Base):
    __tablename__ = "hommepolitique"
    hopol_id = Column(String, primary_key=True)
    role_actuel=Column(String)#Est ce que c'est un député ou un senateur
    prenom=Column(String)
    nom=Column(String)
    date_naissance = Column(Date)
    profession=Column(String)
    profession_cat=Column(String)
    organes = relationship("OrganeRelation", back_populates="hopol")
    activites = relationship("Activite",back_populates="hopol")
    role = relationship("Role",back_populates="hopol")
    appart_parti = relationship("AppartenanceParti",back_populates="hopol")
#L'appartenance a un organe parlementaire
class Organe(Base):
    __tablename__ = "organe"
    organe_id=Column(String,primary_key=True)
    nom=Column(String)
    type=Column(String)
    code_type = Column(String)
    debut=Column(Date)
    fin=Column(Date)
    membres = relationship("OrganeRelation" , back_populates="organe")

#Un lien vers une "activité" un vote une participation a un débat ect on retrouve le detail dans la base mongoDB
class Activite(Base):
    __tablename__="activite"
    activite_id=Column(String,primary_key=True)
    nom=Column(String)
    date=Column(Date)
    type=Column(String)
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"))
    hopol = relationship("HommePolitique",back_populates="activites")

class OrganeRelation(Base):
    __tablename__ = "organe_relation"
    organe_id=Column(String,ForeignKey("organe.organe_id"),primary_key=True)
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    date_debut=Column(Date)
    date_fin=Column(Date)
    hopol = relationship("HommePolitique",back_populates="organes")
    organe = relationship("Organe",back_populates="membres")

#Est ce que c'est un député ou un senateur , quand est qu'il a été élu etc
class Role(Base):
    __tablename__="role"
    id=Column(Integer,primary_key=True)
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"))
    role_name = Column(String)
    date_election=Column(Date)
    id_election=Column(String)#Un id vers la base mongoDB qui contient l'election 
    hopol = relationship("HommePolitique",back_populates="role")

class PartiPolitique(Base):
    __tablename__="partipolitique"
    id=Column(String,primary_key=True)
    nom = Column(String)
    date_creation = Column(Date)
    membres = relationship("AppartenancePartie",back_populates="parti")

class AppartenanceParti(Base):
    __tablename__="appartenanceparti"
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    partie_id=Column(String,ForeignKey("partipolitique.id"),primary_key=True)
    date_appartenance = Column(Date)
    date_quitte = Column(Date)
    hopol = relationship("HommePolitique",back_populates="appart_parti")
    parti = relationship("PartiPolitique",back_populates="membres")