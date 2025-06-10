import os,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from db.mongoDB import mongoConnection
import requests
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

    codecomplet=codedepartement+codecirconscriptionclean
    url=baseurl+rid+"/data/"
    parameters = {parametercirc:codecomplet}
    requete = requests.get(url,params=parameters)

    if(requete.status_code==200):
        return requete.json()
    else:
        print(f"Erreur dans la requete mauvais status code : {requete.status_code}")
        #Bug sur la connection
        return

def get_formated(retour):
    if(retour["data"]==None):
        return
    if(retour["data"][0]==None):
        return
    return retour["data"][0]