from fastapi import APIRouter , Depends , Request
from userManagement import userAccess
from dependencies import require_roles_any

router = APIRouter(dependencies=[Depends(require_roles_any(["admin"]))])

roles = ["admin","guest","users"]

@router.get("/list_users")
async def list_users(request:Request):
    users = userAccess.get_users()
    count = len(users)
    return {"status":"success","message":"Liste des utilisateurs","data":users,"count":count}

router.put("/add_role/{userName}/{role}")
async def add_role(request:Request,userName:str,role:str):
    try:
        userAccess.add_role_user(userName,role)
    except:
        #TODO
        pass

router.put("/remove_role/{userName}/{role}")
async def add_role(request:Request,userName:str,role:str):
    try:
        userAccess.remove_role_user(userName,role)
    except:
        #TODO
        pass