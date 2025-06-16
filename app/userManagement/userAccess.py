from db.mongoDB.mongoConnection import get_connection
from db.mongoDB.mongoOperation import find_dual
from userManagement.security import get_password_hash , verify_password
import os
from fastapi import HTTPException, status
userDBName = os.getenv("MONGO_USER_DB")
class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "A user with this username already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

def sign_user(useName,password):
    user = get_user(useName)
    if user:
        raise UserAlreadyExistsException()
    hashedPassword = get_password_hash(password)
    userInfo = {"username":useName,"hashed_password":hashedPassword,"roles":["guest"]}
    InsertUser(userInfo)

def get_user(useName):  
    found = find_dual("users",userDBName,filter={"username":useName})
    if(len(found)>0):
        return found[0]
    
def get_users():
    found = find_dual("users",userDBName,projection={"username":1,"roles":1})
    return found

def InsertUser(userInfo):
    with get_connection() as client:
        client[userDBName]["users"].insert_one(userInfo)

def add_role_user(userName,role):
    with get_connection() as client:
        collection = client[userDBName]["users"]
        collection.update_one(
        {"username": userName},
        {"$addToSet": {"roles": role}}
        )

def remove_role_user(userName,role):
    with get_connection() as client:
        collection = client[userDBName]["users"]
        collection.update_one(
        {"username": userName},
        {"$pull": {"roles": role}}
        )
