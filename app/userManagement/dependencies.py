from fastapi import Depends ,HTTPException
from typing import List
from .auth import get_user_data

def require_roles_any(required_roles: List[str]):
    def role_checker(user_data=Depends(get_user_data)):
        user_roles = user_data.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user_data
    return role_checker

def require_roles_all(required_roles:List[str]):
    def role_checker(user_data=Depends(get_user_data)):
        user_roles = user_data.get("roles", [])
        for role in required_roles:
            if not role in user_roles:
                raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return user_data
    return role_checker
