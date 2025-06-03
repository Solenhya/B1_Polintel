from pymongo import UpdateOne
from .mongoConnection import get_connection
import os

def insert_bulk(listedictId,listeValue,valueName,client,dbName,collectionName):
    """Une fonction d'insertion en bulk qui prend en parametres deux listes la premiere un dictionaire qui contient les ids et le deuxieme les valeurs a mettre dans le field valuename"""
    operations = [UpdateOne({"_id":dictId["_id"]},{"$set": {valueName: new_value}}) for dictId, new_value in zip(listedictId, listeValue)]
    collection = client[dbName][collectionName]
    collection.bulk_write(operations)


    #Give a simplified tool where 
def find_dual(collection,filter={},projection={},client=None):
    """
    Deux comportement si on donne une connection qui est gerer a l'exterieur on renvoie le curseur sinon on renvoie une liste de résultat
    En créant et fermant une connection
    """
    close = False
    #Si on n'a pas donner de client on creer une connection et on la ferme
    if(client==None):
        close = True
        client = get_connection()
        print("connection creer")
    dbName = os.getenv("MONGO_DBNAME")

    cursor = client[dbName][collection].find(filter=filter,projection=projection)
    if(close):
        retour = []
        for i in cursor:
            retour.append(i)
        client.close()
        return retour
    return cursor