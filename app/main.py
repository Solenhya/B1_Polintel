from fastapi import FastAPI , Request
from fastapi.exceptions import RequestValidationError
import os,sys
#This is so Fing backward and dumb and not consistent WTF
project_dir = os.path.join(os.path.dirname(__file__), "..")
#sys.path.append(project_dir)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routers import admin_user,data_management,users_route
from exceptions.customExceptions import NoTokenException,DatabaseError
from schemas import response_model
import time
import logging
# La configuration de base du logger
logging.basicConfig(
    filename='log.log',
    level=logging.ERROR,  # or INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(title="API Polintel",
    description="Une API qui expose de la donnée sur les hommes politiques",
    version="1.0.0")
app.include_router(users_route.router,tags=["users"])
app.include_router(data_management.router,tags=["data"])
app.include_router(admin_user.router,tags=["admin_user"])


from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.utils import get_openapi

TOKEN_NAME = "token"
api_key_header = APIKeyHeader(name=TOKEN_NAME)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Polintel",
        version="1.0",
        description="Une API qui expose de la donnée sur les hommes politiques",
        routes=app.routes,
    )
    # Add the security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "TokenAuth": {
            "type": "apiKey",
            "in": "header",
            "name": TOKEN_NAME,
        }
    }
    # Add security requirement globally
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"TokenAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/",tags=["test"])
async def root():
    return {"message": "Bonjour Polintel !"}

@app.get("/health",tags=["check"])
async def health():
    logger.info("Connection sur health")
    return{"status":"ok"}

@app.get("/test",tags=["check"])
async def check():
    reponse = response_model.success_response(message="Test")
    return reponse

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


"""FastAPI exception handler attrape les erreur automatiquement mais on peut s'inserer entre les deux et definir nos propre handler.FastAPI choisi le plus precis si il trouve puis il remonte l'arborescence d'heritage. Par exemple Credential(HTTPException) avant HTTPException avant Exception"""

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """La gestion d'une erreur de validation pydantic. Utiliser principalement dans les inputs utilisateur"""
    response = response_model.error_response(f"Erreur dans la validation de donnée : {exc.errors()}")
    return response

@app.exception_handler(NoTokenException)
async def notoken_excepttion_handler(request:Request,erreur:NoTokenException):
    reponse = response_model.error_response(erreur.message)
    return reponse

@app.exception_handler(DatabaseError)
async def dberror_exception_handler(request:Request,erreur:DatabaseError):
    reponse = response_model.error_response(erreur.message)
    return reponse

@app.exception_handler(Exception)
async def erreur_exception_handler(request:Request,erreur:Exception):
    reponse = response_model.error_response(message=str(erreur))
    return reponse