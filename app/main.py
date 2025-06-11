from fastapi import Depends, FastAPI , Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from userManagement.auth import get_current_user


app = FastAPI(    title="API Polintel",
    description="Une API qui expose de la donnée sur les hommes politiques",
    version="1.0.0")




@app.get("/",tags=["redirection"])
async def root():
    response = RedirectResponse(url="/login", status_code=303)
    return response
    return {"message": "Hello MoocAI Applications!"}

@app.get("/health",tags=["check"])
async def health():
    return{"status":"ok"}