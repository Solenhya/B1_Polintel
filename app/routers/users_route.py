from fastapi import APIRouter , Depends , Request , Body
from userManagement import userAccess , auth
from userManagement.dependencies import require_roles_any
from schemas import response_model
from pydantic import BaseModel , Field
from fastapi import APIRouter, HTTPException
from typing import Optional
from exceptions.customExceptions import IncorrectInputException
from db.mongoDB.mongoConnection import get_connection
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

dbName = os.getenv("MONGO_USER_DB")

class LoginRequest(BaseModel):
    username: str
    password: str

class SignUpRequest(BaseModel):
    username:str
    password:str
    comfirm_password:str
    email:str

class RemoveRequest(BaseModel):
    username:str
    password:str
    delete_reason:Optional[str]=Field(None,description="Votre raison pour supprimer votre compte")

router = APIRouter()

@router.post("/connect")
async def connect(loginrequest:LoginRequest):
    userName = loginrequest.username
    password = loginrequest.password
    retour = await auth.login_for_access_token(userName,password)
    with get_connection() as client:
        print(dbName)
        collection = client[dbName]["users"]
        currentdate = datetime.now()
        result = collection.update_one({"username":userName},{"$set":{"lastactive":currentdate}})
        print(f"{userName} and {currentdate} et result {result.matched_count}")
    return retour

@router.post("/sign-up")
async def sign_up(signRequest:SignUpRequest):
    username = signRequest.username
    password = signRequest.password
    comfirm = signRequest.comfirm_password
    email = signRequest.email
    if(password!=comfirm):
        reponse = response_model.error_response(f"Erreur pour la creation de l'utilisateur {username} sur la comfirmation du mot de passe")
        return reponse
    userAccess.sign_user(username,password,email)
    return response_model.success_response(message=f"L'utilisateur {username} a bien été creer")

@router.delete("/remove-user")
async def remove_user(request:Request,removedata : RemoveRequest=Body(...)):
    user = auth.get_current_user(request)
    userdelete= removedata.username
    if(user!=userdelete):
        raise IncorrectInputException("User deletion",f"Erreur dans la suppresion d'un utilisateur! Vous devez etre connecté ")
    userdb = userAccess.get_user(user)
    if(not userdb):
        raise IncorrectInputException("User deletion",f"Erreur lors de la tentative de suppression d'un utilisateur. Cet utilisateur n'existe pas")
    if(userdb["hashed_password"]!=removedata.password):
        raise IncorrectInputException("User deletion",f"Erreur lors de la suppresion d'un utilisateur! Le mot de passe renseigner n'est pas correcte")
    if removedata.delete_reason:
        delete_reason = removedata.delete_reason
    else:
        delete_reason = "Pas d'explication a été fourni"
    userAccess.delete_user(user)
    logger.info(f"Suppression de l'utilisateur {user}! Raison : {delete_reason}")