import os
import requests
import io 
import zipfile



def download_brut(url,exactPath):
    response = requests.get(url)
    #Recupere le resultat de la requete sous format binaire et 
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    extract_path = exactPath
    os.makedirs(extract_path, exist_ok=True)
    zip_file.extractall(extract_path)
    print(f"Fichiers des députés extrait vers : {extract_path}")