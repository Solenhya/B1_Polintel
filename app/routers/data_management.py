from fastapi import APIRouter , Depends , Request
from userManagement import userAccess
from userManagement.dependencies import require_roles_any
from schemas import response_model
from depute import assemble_file_recuperation,recuperation_election,depute_organe,vote_depute,dec_interet_patri,clean_organe_date
router = APIRouter(dependencies=[Depends(require_roles_any(["admin"]))])

@router.post("/depute_extract_data")
async def import_depute(request:Request):
    assemble_file_recuperation.full_import()
    response = response_model.success_response(message=f"Recuperation des données députes fait avec success")
    return response

@router.post("/depute_insertion_postgre")
async def postgre_import(request:Request):
    count = depute_organe.full_import()
    response = response_model.success_response(message=f"Insertion députes dans postgre fait avec success",count=count)
    return response

@router.post("/depute_election")
async def depute_creation_election(request:Request):
    count = recuperation_election.process_elections()
    response = response_model.success_response(message=f"Creation des documents elections depute fait avec success",count=count)
    return response   

@router.post("/vote_depute")
async def import_vote_depute(request:Request):
    vote_depute.start_import_vote()
    response = response_model.success_response(message=f"Recuperation des données des votes des députes fait avec success")
    return response
    
@router.post("/declaration_financiere")
async def import_declaration_money(request:Request):
    success,total = dec_interet_patri.proccess_all()
    if success>0:
        response = response_model.success_response(message=f"Traitement de l'import des declarations d'interet et de patrimoine des députés fait {success}success / {total} a traité")
    else:
        response = response_model.error_response(message=f"Echec dans l'import des declaration d'interet et de patrimoine des députés {success}/{total} on pu etre traité")
    return response

@router.post("/clean_organe")
async def clean_organe(request:Request):
    success,total = clean_organe_date.fill_up_from_member()
    if(success>0 or total==0):
        response = response_model.success_response(message=f"Traitement du remplissage des dates de début d'organe vide fait {success}success / {total} a traité")
    else:
        response = response_model.error_response(message=f"Echec dans le remplissage des dates de début d'organe. Aucun entrée n'a pu etre rempli sur {total}")
    return response