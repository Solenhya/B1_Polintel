from fastapi import APIRouter , Depends , Request
from userManagement import userAccess
from userManagement.dependencies import require_roles_any
from schemas import response_model
router = APIRouter(dependencies=[Depends(require_roles_any(["admin"]))])

roles = ["admin","guest","users"]

@router.get("/list_users")
async def list_users(request:Request):
    users = userAccess.get_users()
    print(users)
    count = len(users)
    response = response_model.success_response(users,"Liste des utilisateurs",count)
    return response
    return {"status":"success","message":"Liste des utilisateurs","data":users,"count":count}

@router.put("/add_role/{userName}/{role}")
async def add_role(request:Request,userName:str,role:str,user = Depends(require_roles_any(["admin"]))):
    userAccess.add_role_user(userName,role)
    response = response_model.success_response(message=f"Ajout du role {role} a {userName} fait avec success")
    return response

@router.put("/remove_role/{userName}/{role}")
async def add_role(request:Request,userName:str,role:str):
    userAccess.remove_role_user(userName,role)
    response = response_model.success_response(message=f"Ajout du role {role} a {userName} fait avec success")
    return response 