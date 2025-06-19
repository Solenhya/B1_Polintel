from sqlalchemy import Column, Integer, String, DateTime,ForeignKey,Date , Table , UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

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
    votes = relationship(
    "VoteRelation",
    back_populates="hopol"
    )
    declarations_money= relationship("DeclarationMoney",back_populates="hopol")
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
    votes = relationship("Vote",back_populates="vote_origine")#Les votes qui on eu lieu dans cette organe.(Assemble par exemple)
    vote_organes = relationship("VoteRelation",back_populates="organe_parlementaire")

#Un lien un vote. L'id utiliser est le meme que dans la base de donnée mongo qui peut contenir plus d'information
class Vote(Base):
    __tablename__="vote"
    vote_id=Column(String,primary_key=True)
    nom=Column(String)
    date=Column(Date)
    resultat=Column(String,comment="Est ce que le vote est passer ou pas. Adopté ou Non-Adopté")
    nombre_votant=Column(Integer)
    suffrage_exprime=Column(Integer)
    vote_requis=Column(Integer)
    type_vote=Column(String,comment="Le type de vote . Pour l'instant peut etre : scrutin public ordinaire, scrutin public solennel ou motion de censure")
    organe_votant = Column(String,ForeignKey("organe.organe_id"))
    hopols = relationship("VoteRelation",back_populates="vote")
    vote_origine = relationship("Organe",back_populates="votes")

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

class VoteRelation(Base):
    __tablename__="vote_relation"
    hopol_id=Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    vote_id = Column(String,ForeignKey("vote.vote_id"),primary_key=True)
    position = Column(String,comment="Est ce qu'il s'agit d'un vote pour , contre , nonvotant ou abstention ")
    groupe_parlementaire=Column(String,ForeignKey("organe.organe_id"),comment="Sous quel groupe parlementaire")
    hopol = relationship("HommePolitique",back_populates="votes")
    vote = relationship("Vote",back_populates="hopols")
    organe_parlementaire = relationship("Organe",back_populates="vote_organes")
#Si je veux rajouter la position des groupes parlementaire refaire une table qui relis organe (ou sont les goupes parlementaire) et ajouter la dedans la position majoritaire

class DeclarationMoney(Base):
    __tablename__="declaration_moneitaire"
    decl_id = Column(Integer, primary_key=True, autoincrement=True)
    hopol_id=Column(String,ForeignKey("hommepolitique.hopol_id"))
    date_traitement=Column(Date,comment="a quel date a t on fait le traitement")
    type_declaration = Column(String,comment="Quel type de declaration est ce que c'est : declaration d'interet ou declaration de patrimoine ect")
    status=Column(String,comment="Quel est le status de l'information. Est ce que l'information est :accessible, déposé et bientot publié,en cours,pas envoye,accessible en prefecture")
    id_mongo=Column(String,comment="L'identifiant dans la base de donnée mongo pour l'information en brut")
    hopol = relationship("HommePolitique",back_populates="declarations_money")
