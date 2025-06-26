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
    elections = relationship("Election",back_populates="hopol")
    def dict_unit(self):
        retour = self.__dict__.copy()#Fonction automatique pour transformer un model en dictionaire
        retour.pop("_sa_instance_state")#Est inclus un objet d'instance que l'on doit retirer pour que le message soit plus clair

        #TODO
    def to_dict(self,source=None):
        if not source:
            dataretour = self.__dict__.copy()
            dataretour.pop("_sa_instance_state")
            dataretour["date_naissance"] = dataretour["date_naissance"].isoformat()#Convertit en string pour json
            listorgane=[]
            for organe in self.organes:
                data = organe.to_dict(source="hopol")
                listorgane.append(data)
            dataretour["appartenance_organes"]=listorgane
            listVote = []
            for vote in self.votes:
                data = vote.to_dict(source ="hopol")
                listVote.append(data)
            dataretour["votes"]=listVote
            listElection = []
            for election in self.elections:
                data = election.to_dict(source="hopol")
                listElection.append(data)
            dataretour["elections"]=listElection
            listdeclaration = []
            for declaration in self.declarations_money:
                data = declaration.to_dict(source="hopol")
                listdeclaration.append(data)
            dataretour["declarations"]=listdeclaration

        return dataretour
    
    #Methode static qui permets depuis la classe de connaitre les collonnes qui pourait rentrer en conflict lors d'un upsert
    @staticmethod
    def get_conflict_col():
        return["hopol_id"]    
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
    elections = relationship("Election",back_populates="poste")
    
    def to_dict(self,source=None):
        data={}
        if(source=="simple"):
            data["nom"]=self.nom
            data["type"]=self.code_type
        return data

    @staticmethod
    def get_conflict_col():
        return["organe_id"]    
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

    def to_dict(self,source=None):
        dataretour={}
        if(source=="simple"):
            dataretour["nom"]=self.nom
            dataretour["date_vote"]=self.date.isoformat()#Convertit en string
            dataretour["resultat"]=self.resultat
            dataretour["nombre_votant"]=self.nombre_votant
            dataretour["type_vote"]=self.type_vote
        return dataretour
    @staticmethod
    def get_conflict_col():
        return ["vote_id"]

class OrganeRelation(Base):
    __tablename__ = "organe_relation"
    organe_id=Column(String,ForeignKey("organe.organe_id"),primary_key=True)
    hopol_id = Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    date_debut=Column(Date,primary_key=True)
    date_fin=Column(Date)
    qualite=Column(String,comment="En quel qualité il appartient a l'organisation (membres,président ect)",primary_key=True)
    hopol = relationship("HommePolitique",back_populates="organes")
    organe = relationship("Organe",back_populates="membres")

    def to_dict(self,source=None):
        data = {}
        #TODO complété pour les differentes sources
        if(source=="hopol"):
            data["date_debut"]=self.date_debut.isoformat()#Convert en str pour json
            if(self.date_fin):
                data["date_fin"]=self.date_fin.isoformat()#Convert en str pour json
                
            else:
                data["date_fin"]="En cours"
            data["role"]=self.qualite
            data["organe"]=self.organe.to_dict(source="simple")
        return data
    @staticmethod
    def get_conflict_col():
        return["organe_id","hopol_id","date_debut","qualite"]

class VoteRelation(Base):
    __tablename__="vote_relation"
    hopol_id=Column(String,ForeignKey("hommepolitique.hopol_id"),primary_key=True)
    vote_id = Column(String,ForeignKey("vote.vote_id"),primary_key=True)
    position = Column(String,comment="Est ce qu'il s'agit d'un vote pour , contre , nonvotant ou abstention ")
    groupe_parlementaire=Column(String,ForeignKey("organe.organe_id"),comment="Sous quel groupe parlementaire")
    hopol = relationship("HommePolitique",back_populates="votes")
    vote = relationship("Vote",back_populates="hopols")
    organe_parlementaire = relationship("Organe",back_populates="vote_organes")

    def to_dict(self,source=None):
        dataretour = {}
        if(source=="hopol"):

            dataretour["position"]=self.position
            dataretour["groupe_parlementaire"]=self.organe_parlementaire.to_dict(source="simple")
            dataretour["scrutins"]=self.vote.to_dict(source="simple")
        return dataretour

    @staticmethod
    def get_conflict_col():
        return ["hopol_id","vote_id"]

class DeclarationMoney(Base):
    __tablename__="declaration_moneitaire"
    decl_id = Column(Integer, primary_key=True, autoincrement=True)
    hopol_id=Column(String,ForeignKey("hommepolitique.hopol_id"))
    date_traitement=Column(Date,comment="a quel date a t on fait le traitement")
    type_declaration = Column(String,comment="Quel type de declaration est ce que c'est : declaration d'interet ou declaration de patrimoine ect")
    status=Column(String,comment="Quel est le status de l'information. Est ce que l'information est :accessible, déposé et bientot publié,en cours,pas envoye,accessible en prefecture")
    id_mongo=Column(String,comment="L'identifiant dans la base de donnée mongo pour l'information en brut")
    hopol = relationship("HommePolitique",back_populates="declarations_money")

    def to_dict(self,source=None):
        data = {}
        data["decl_id"]=self.decl_id
        data["date_traitement"]=self.date_traitement.isoformat()
        data["type_declaration"]=self.type_declaration
        data["status"]=self.status
        data["id_mongo"]=self.id_mongo


    @staticmethod
    def get_conflict_col():
        return ["decl_id"]

class Election(Base):
    __tablename__="election"
    id_election = Column(Integer,primary_key=True,autoincrement=True,comment="La clef primaire qui est aussi la clef mongo pour l'ensemble des informations")
    organe_id=Column(String,ForeignKey("organe.organe_id"))
    nom_complet = Column(String,comment="Le nom obtenu en concatenant le numero de circonscription et le département")
    date_election = Column(Date,comment="La date de l'élection")
    nbr_inscrit=Column(Integer,comment="Le nombre d'inscrit")
    nbr_votant=Column(Integer,comment="Le nombre de personne qui ont voté")
    nbr_blancs=Column(Integer,comment="Le nombre de vote blanc")
    gagnant_id = Column(String,ForeignKey("hommepolitique.hopol_id"),comment="La clef étrangere vers l'homme politique qui a gagner cette election")
    gagnant_voix=Column(Integer,comment="Le nombre de voix obtenu par le gagnant de l'election")
    runnerup_name = Column(String,comment="A default d'avoir l'id on précise le nom du candidat arriver en deuxieme")
    runnerup_voix = Column(Integer,comment="Le nombre de voix obtenu par le deuxieme candidat")
    hopol = relationship("HommePolitique",back_populates="elections")
    poste = relationship("Organe",back_populates="elections")

    def to_dict(self,source=None):
        dataretour={}
        if source=="hopol":
            dataretour = self.__dict__.copy()
            dataretour["nom"]=self.nom_complet
            dataretour["date_election"]=dataretour["date_election"].isoformat()
            dataretour.pop("_sa_instance_state")
        return dataretour

    @staticmethod
    def get_conflict_col():
        return ["id_election"]