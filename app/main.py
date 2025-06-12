from fastapi import Depends, FastAPI , Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os,sys
#This is so Fing backward and dumb and not consistent WTF
project_dir = os.path.join(os.path.dirname(__file__), "..")
#sys.path.append(project_dir)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from userManagement import auth
from userManagement.auth import get_current_user
import time

app = FastAPI(title="API Polintel",
    description="Une API qui expose de la donnée sur les hommes politiques",
    version="1.0.0")


@app.get("/",tags=["test"])
async def root():
    return {"message": "Bonjour Polintel !"}

@app.get("/health",tags=["check"])
async def health():
    return{"status":"ok"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response