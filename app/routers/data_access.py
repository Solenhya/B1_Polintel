from fastapi import APIRouter , Depends , Request
from userManagement.dependencies import require_roles_any
from db.data_find import BaseHopolRequest , BaseOrganeRequete , BaseVoteRequete
from db.data_find import get_hopols , get_organes,get_votes , get_hopol_info , get_mongo_document
from schemas import response_model

router = APIRouter(dependencies=[Depends(require_roles_any(["admin","user"]))])

@router.get("/hopols")
async def endpoint_hopols(request_data:BaseHopolRequest=Depends()):
    data = get_hopols(request_data)
    reponse = response_model.success_response(data=data,message="Liste des hommes politiques avec parametres")
    return reponse

@router.get("/organes")
async def endpoint_organes(request_data:BaseOrganeRequete=Depends()):
    data = get_organes(request_data)
    reponse = response_model.success_response(message="Liste des organes par parametres",data=data)
    return reponse

@router.get("/votes")
async def endpoint_votes(request_data:BaseVoteRequete=Depends()):
    data = get_votes(request_data)
    reponse = response_model.success_response(message="Liste des votes par parametres",data=data)
    return reponse

@router.get("/hopol_info")
async def endpoint_hopol_info(request_data:BaseHopolRequest=Depends()):
    data = get_hopol_info(request_data)
    reponse = response_model.success_response(message="Liste des hommes politiques et toute leurs information",data=data)
    return reponse

@router.get("/consulte_declaration/{declaration_id}")
async def consult_declaration(declaration_id:str,role = Depends(require_roles_any(["admin"]))):
    document = get_mongo_document("declaration-monetaire",declaration_id)
    reponse = response_model.success_response(message=f"Declaration",data=document)
    return reponse

