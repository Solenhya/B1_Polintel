from fastapi import APIRouter , Depends , Request
from userManagement.dependencies import require_roles_any

router = APIRouter(dependencies=[Depends(require_roles_any(["admin","user"]))])

