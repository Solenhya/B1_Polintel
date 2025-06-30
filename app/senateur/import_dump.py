import psycopg2
import subprocess
import os ,sys
project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from dotenv import load_dotenv
load_dotenv()
from utils.file_download import download_brut
from db.postgreSQL.db_connection import get_connection_dump
from exceptions.customExceptions import ScrappingFormatException
senateurfolder="senateurs"
url_download = "https://data.senat.fr/data/senateurs/export_sens.zip"

senateurvotefolder = "votes_senateur"
url_download_vote="https://data.senat.fr/data/dosleg/dosleg.zip"
def download_dump_senateur():
    fullPath =  os.path.join(get_extract_path(),senateurfolder)
    download_brut(url_download,fullPath)

def import_dump_senateur():
    folder_path = os.path.join(get_extract_path(),senateurfolder)
    # Recuperé les fichiers
    all_files = os.listdir(folder_path)

    # Filtré sur les .sql
    sql_files = [file for file in all_files if file.endswith('.sql')]
    if len(sql_files)!=1:
        raise ScrappingFormatException(origine="Récuperation dump senateur",message=f"Erreur dans les fichiers sql 1 fichier attendu mais on a {sql_files}")
    full_path = os.path.join(folder_path,sql_files[0])
    import_from_dump(full_path)

def import_from_dump(filePath):
        #Définir la variable d'environnement PGPASSWORD uniquement pour cette commande
    env = os.environ.copy()
    env['PGPASSWORD'] = os.getenv("SQL_PASSWORD")
    # Construire la commande
    command = [
        os.getenv("PSQL_EXEC"),
        "-h", os.getenv("SQL_HOST"),
        "-p", os.getenv("SQL_PORT"),
        "-U", os.getenv("SQL_USER"),
        "-d", os.getenv("SQL_DATABASE_DUMP"),
        "-f", filePath
    ]
    # Exécuter la commande
    result = subprocess.run(command, env=env, capture_output=True, text=True)

    print(result.stdout)
    # Afficher le résultat
    if result.returncode == 0:
        print("Importation terminée avec succès.")
    else:
        print("Erreur lors de l'importation.")
        print(result.stderr)

def download_dump_vote():
    fullPath =  os.path.join(get_extract_path(),senateurvotefolder)
    download_brut(url_download_vote,fullPath)
    print("Votes senateur éffectuer avec succes")

def import_senateur_vote():
    folder_path = os.path.join(get_extract_path(),senateurvotefolder)
    # Recuperé les fichiers
    all_files = os.listdir(folder_path)

    # Filtré sur les .sql
    sql_files = [file for file in all_files if file.endswith('.sql')]
    if len(sql_files)!=1:
        raise ScrappingFormatException(origine="Récuperation dump senateur",message=f"Erreur dans les fichiers sql 1 fichier attendu mais on a {sql_files}")
    full_path = os.path.join(folder_path,sql_files[0])
    import_from_dump(full_path)

#Doit etre présent dans le fichier ou l'on souhaite importer les fichiers (A revoir mais manipulation de path python c'est ...)
def get_extract_path():
    extract = os.path.dirname(os.path.abspath(__file__))
    return extract

if __name__=="__main__":
    #download_dump()
    #import_dump_senateur()
    #download_dump_vote()
    import_senateur_vote()