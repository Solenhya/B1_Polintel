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
        #Bug trop long
        return
    if(taillecircons<1):
        #Bug trop court
        return
    if(taillecircons==1):
        #Il manque le 0 devant
        codecirconscriptionclean="0"+codecirconscriptionclean

    codecomplet=codedepartement+codecirconscriptionclean
    url=baseurl+rid
    params = {parametercirc:codecomplet}
    requete = requests.get(url,parameters=params)

    if(requete.status_code==200):
        return requete.content
    else:
        #Bug sur la connection
        return
    