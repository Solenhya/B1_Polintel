from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Date , Table
from sqlalchemy.orm import relationship
from .database import Base

activite_hopol_association = Table(
    "activite_hopol_association",
    Base.metadata,
    Column("hopol_id", String, ForeignKey("hommepolitique.hopol_id"),primary_key=True),
    Column("activite_id", String, ForeignKey("activite.activite_id"),primary_key=True)
)

#La définition des table postgre via sqlalchemy models
class HommePolitique(Base):
    __tablename__ = "hommepolitique"
    hopol_id = Column(String, primary_key=True)
    prenom=Column(String)
    nom=Column(String)
    date_naissance = Column(Date)
    profession=Column(String)
    profession_cat=Column(String)
    organes = relationship("OrganeRelation", back_populates="hopol")
    #Ajout de la table de liaison n-n
    activites = relationship(
    "Activite",
    secondary=activite_hopol_association,#Precise pour l'orm comment trouvé le activité (un model Activite)
    back_populates="hommes_politiques"
    )
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
    hommes_politiques = relationship(
    "HommePolitique",
    secondary=activite_hopol_association,
    back_populates="activites"
    )


class OrganeRelation(Base):
    __tablename__ = "organe_relation"
    organe_id=Column(String,ForeignKey("organe.organe_id"),primary_key=True)
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    date_debut=Column(Date,primary_key=True)
    date_fin=Column(Date)
    access_id=Column(String,comment="Une clef vers l'information d'acces au poste dans une base mongoDB")
    access_type=Column(String,comment="De quel facon il a acceder a cette organe")
    qualite=Column(String,comment="En quel qualité il appartient a l'organisation (membres,président ect)",primary_key=True)
    hopol = relationship("HommePolitique",back_populates="organes")
    organe = relationship("Organe",back_populates="membres")
