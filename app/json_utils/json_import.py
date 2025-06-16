import os , sys
import json

project_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(project_dir)
from db.mongoDB import mongoConnection
#Une fonction recursive pour enlever les relicats xml
def clean_json(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            match key:
                case "@xmlns":
                    continue 
                case "@xmlns:xsi":
                    continue  # Supprime
                case "@xsi:type":
                    new_data["type"]=clean_json(value)
                case _:
                    if isinstance(value, dict) and value.get("@xsi:nil") == "true":
                        new_data[key] = None
                    else:
                        new_data[key] = clean_json(value)
        return new_data
    elif isinstance(data, list):
        return [clean_json(item) for item in data]
    else:
        return data

def import_json_file(file_path,databaseName):
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
        except Exception as e:
            print(f"Erreur dans l'ouverture du fichier {e}")
            return
        insert_data = clean_json(data)
        keys = list(insert_data)
        if len(keys)==1:
            collection_name = keys[0]
            insert_data=insert_data[collection_name]
            uid = insert_data["uid"]
            #Si le cleaning du xml a transformer le uid en dict avec un type
            if(type(uid)==dict):             
                try:
                    uid=uid["#text"]
                except Exception as e:
                    print(f"Erreur dans le setting de l'id")
                    print(f"Data : {insert_data["uid"]} type : {type(insert_data["uid"])} from {file_path}")
                    return    
                
            insert_data["_id"]=uid   
            with mongoConnection.get_connection() as client:
                collection = client[databaseName][collection_name]
                collection.update_one(
                    {"_id": insert_data["_id"]},  # cherche l'id et l'upsert 
                    {"$set": insert_data},
                    upsert=True                  
                )

        else:
            #On s'attend a un dictionnaire de type : {nomdecollection:{itemdecollection}}
            print("Erreur dans l'insertion des données. Le format n'est pas celui attendu")

def import_json_folder(folderpath,database):
    list_files = os.listdir(folderpath)
    for file in list_files:
        split = file.split(".")
        filepath = os.path.join(folderpath,file)
        if len(split)==2 and split[1]=="json":#On import le json
            import_json_file(filepath,database)
        elif len(split)==1:#C'est un dossier on doit donc allez plus loin
            import_json_folder(filepath,database)
    print(f"{len(list_files)} Fichiers traités")

