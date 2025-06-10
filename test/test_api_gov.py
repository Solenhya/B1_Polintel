import os,sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Remonte jusqu'au dossier parent MoocAI
sys.path.append(parent_dir)
from app.depute.recuperation_election import get_election

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