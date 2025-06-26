from db.mongoDB.mongoConnection import get_connection
from db.mongoDB.mongoOperation import find_dual
from userManagement.security import get_password_hash , verify_password
import os
from fastapi import HTTPException, status
from exceptions.customExceptions import DatabaseError
from datetime import datetime
userDBName = os.getenv("MONGO_USER_DB")
class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "A user with this username already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

def sign_user(useName,password,userEmail):
    check_user_similar(useName,userEmail)
    hashedPassword = get_password_hash(password)
    currentdate = datetime.now()
    userInfo = {"username":useName,"email":userEmail,"hashed_password":hashedPassword,"roles":["guest"],"lastactive":currentdate}
    InsertUser(userInfo)

def get_user(useName):  
    found = find_dual("users",userDBName,filter={"username":useName},projection={"_id":0})
    if(len(found)>0):
        return found[0]
    
def check_user_similar(userName,email):
    querry = {
    "$or": [
        {"username": userName},
        {"email": email}
    ]
    }
    found = find_dual("users",userDBName,filter=querry)
    if(len(found)==0):
        return
    if(len(found)==1):
        if(found["username"]==userName):
            raise UserAlreadyExistsException()
        if(found["email"]==email):
            raise UserAlreadyExistsException(detail="A user with this email already exist")
    else:
        raise UserAlreadyExistsException()
def get_users():
    found = find_dual("users",userDBName,projection={"username":1,"email":1,"roles":1,"_id":0})
    return found

def InsertUser(userInfo):
    with get_connection() as client:
        client[userDBName]["users"].insert_one(userInfo)

def add_role_user(userName,role):
    with get_connection() as client:
        collection = client[userDBName]["users"]
        try:
            collection.update_one(
        {"username": userName},
        {"$addToSet": {"roles": role}}
        )
        except Exception as e: 
            raise DatabaseError("Add userRole",userDBName,"users",e)

def remove_role_user(userName,role):
    with get_connection() as client:
        collection = client[userDBName]["users"]
        try:
            collection.update_one(
        {"username": userName},
        {"$pull": {"roles": role}}
        )
        except Exception as e: 
            raise DatabaseError("Remove userRole",userDBName,"users",e)
        
def delete_user(username):
    with get_connection() as client:
        collection = client[userDBName]["users"]
        try:
            collection.delete_one({"username":username})
        except Exception as e:
            raise DatabaseError("Remove user",userDBName,"users",e)
