import os,sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Remonte jusqu'au dossier parent
sys.path.append(parent_dir)
from app.depute.recuperation_election import get_election , create_elec_obj,get_formated

def testBase():
    requete = get_election("1","01")
    print(requete)
    assert requete!=None

def testErreur():
    requete = get_election("bonjour","bla")
    assert requete==None

def testFormat():
    requete = get_election("1","01")
    print(type(requete))
    assert type(requete)==dict
    data = requete["data"]
    assert data!=None
    print(type(data))
    assert data[0]!=None

def testFormatageSimple():
    testValue = {"bla":"blabla","moooh":"vache","bla 1":"blo","bla 2":"pla","bli 1":"bli","bli 2":"blie","__id":"C'est moi l'id"}
    retour = create_elec_obj(testValue)
    print(retour)
    assert retour["moooh"]=="vache"
    assert len(retour["candidats"])==2
    assert len(retour["candidats"][0])==2

def testFormatage():
    retour=get_formated(get_election("1","01"))
    elec_obj = create_elec_obj(retour)
    print(elec_obj)
    assert elec_obj!=None
    assert len(elec_obj["candidats"])>0
    assert "Nom candidat" in elec_obj["candidats"][0]
    assert "Prénom candidat" in elec_obj["candidats"][0]
    assert "Sexe candidat" in elec_obj["candidats"][0]
    assert "Voix" in elec_obj["candidats"][0]
    assert "% Voix/inscrits" in elec_obj["candidats"][0]
    assert "% Voix/exprimés" in elec_obj["candidats"][0]
    assert "Numéro de panneau" in elec_obj["candidats"][0]
    