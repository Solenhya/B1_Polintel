import requests
import zipfile
import io
import os , sys
import json

project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from db.mongoDB import mongoConnection , mongoOperation
from dotenv import load_dotenv
load_dotenv()
from json_utils import json_import

URL_LISTE="https://data.assemblee-nationale.fr/acteurs/deputes-en-exercice"
#URL_BRUT="https://data.assemblee-nationale.fr/static/openData/repository/17/amo/acteurs_mandats_organes_divises/AMO50_acteurs_mandats_organes_divises.json.zip"
URL_DEPUTE_LIST="https://data.assemblee-nationale.fr//static/openData/repository/17/amo/deputes_actifs_mandats_actifs_organes/AMO10_deputes_actifs_mandats_actifs_organes.json.zip"
URL_COLAB_LIST="https://data.assemblee-nationale.fr/static/openData/repository/17/amo/collaborateurs_csv_opendata/liste_collaborateurs_libre_office.csv"
URL_VOTE="https://data.assemblee-nationale.fr/static/openData/repository/17/loi/scrutins/Scrutins.json.zip"
divBox="feature-box"
deputefolder="depute_files"
votefolder="vote"

def download_file(url,name):
    response = requests.get(url)
    with open(name, "wb") as f:
        f.write(response.content)

def download_brut(url,foldername):
    response = requests.get(url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    extract_path = os.path.join(os.getcwd(),foldername)
    os.makedirs(extract_path, exist_ok=True)
    zip_file.extractall(extract_path)
    print(f"Fichiers des députés extrait vers : {extract_path}")



def insert_list(folder,database,forceName=None):
    """Fonction pour inserer les fichiers .json contenue dans un dossier
    keepbaseName implique que l'on garde le nom de base
    Possibiliter de faire des collection avec nom composer pour éviter deux colllection ayant le meme nom mais pas de la meme source"""


    basefolder = os.path.join(os.getcwd(), folder)
    liste_directory = os.listdir(basefolder)
    basename = folder
    #Doit vérifier qu'on est juste au dessus d'un dossier contenant des .json
    if(liste_directory==["json"]):
        print("dossier json")
        basefolder=os.path.join(basefolder,"json")
        liste_directory=os.listdir(basefolder)
    print(liste_directory)
    for name in liste_directory:
        path = os.path.join(basefolder,name)
        mongoOperation.insert_folder_preproc(name,path,database,json_import.clean_json)
        print(f"{name} Done")

def replace_root(collectionName,databaseName,name):
    
    pipeline = [
    {
        "$replaceRoot": { "newRoot": f"${name}" }
    },
    {
        "$merge": { "into": f"{collectionName}" }
    }
    ]
    with mongoConnection.get_connection() as client:
        collection = client[databaseName][collectionName]
        result = collection.aggregate(pipeline)

def insert_v2(dbName,folderName):
    folderPath = os.path.join(os.getcwd(),folderName)
    json_import.import_json_folder(folderPath,dbName)

if __name__ =="__main__":
    #download_brut(URL_DEPUTE_LIST,deputefolder)
    #insert_list(deputefolder,"depute")
    #download_file(URL_COLAB_LIST,"depute_collab.csv")
    insert_v2("depute",deputefolder)
    insert_v2("depute",votefolder)