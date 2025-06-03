from fastapi import HTTPException , status , Depends ,Request
from fastapi.security import OAuth2PasswordRequestForm,HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from .security import verify_password, create_access_token
from .userAccess import get_user
from jose import JWTError,jwt
from typing import Optional
import os


security = HTTPBearer()

async def login_for_access_token(form_data: OAuth2PasswordRequestForm):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password") 
    # Create and return token
    access_token = create_access_token(data={"sub": form_data.username,"roles":user["roles"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Custom exception for when token is missing or invalid
class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def get_current_user(request:Request):
    token = request.cookies.get("token")
    # Check if the token is empty or None
    if not token:
        raise CredentialsException(detail="Token is missing or empty")
    # Use JWT decoding and validation logic
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException(detail="Token does not contain a valid username")
        return username
    except JWTError as e:
        raise CredentialsException(detail=f"JWT decoding error: {str(e)}")
    
def get_user_data(request:Request):
    token = request.cookies.get("token")
    if not token:
        response = RedirectResponse(url="/login",status_code=401)
        return response
        raise CredentialsException(detail="Token is missing or empty")
    # Use JWT decoding and validation logic
    try:
        user_data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        if user_data is None:
            raise CredentialsException(detail="Token does not contain a valid username")
        return user_data
    except JWTError as e:
        raise CredentialsException(detail=f"JWT decoding error: {str(e)}")