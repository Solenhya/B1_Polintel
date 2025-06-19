from fastapi import APIRouter , Depends , Request
from userManagement import userAccess , auth
from userManagement.dependencies import require_roles_any
from schemas import response_model
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

class LoginRequest(BaseModel):
    username: str
    password: str

class SignUpRequest(BaseModel):
    username:str
    password:str
    comfirm_password:str

router = APIRouter()

@router.post("/connect")
async def connect(loginrequest:LoginRequest):
    userName = loginrequest.username
    password = loginrequest.password
    retour = await auth.login_for_access_token(userName,password)
    return retour

@router.post("/sign-up")
async def sign_up(signRequest:SignUpRequest):
    username = signRequest.username
    password = signRequest.password
    comfirm = signRequest.comfirm_password
    if(password!=comfirm):
        reponse = response_model.error_response(f"Erreur pour la creation de l'utilisateur {username} sur la comfirmation du mot de passe")
        return reponse
    user = userAccess.get_user(username)
    if user:
        reponse = response_model.error_response(f"Erreur dans la création de l'utilisateur {username} il existe deja")
        return reponse
    userAccess.sign_user(username,password)
    return response_model.success_response(message=f"L'utilisateur {username} a bien été creer")