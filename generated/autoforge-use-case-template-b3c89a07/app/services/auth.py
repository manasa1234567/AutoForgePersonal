from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import List
from pydantic import BaseModel

# This is a simplified auth dependency for demonstration
# A real implementation would validate JWT tokens and integrate with MS Entra ID

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    scopes={"openid": "Sign in"}
)

class User(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    roles: List[str]

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # In a real app, decode and verify token and get user info
    # Here return a dummy user for demonstration
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # dummy user based on token (token ignored here)
    user = User(
        id="1",
        username="jane.employee@company.com",
        full_name="Jane Employee",
        email="jane.employee@company.com",
        roles=["employee"]
    )
    return user

def require_role(role: str):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if role not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required role: {role}"
            )
        return current_user
    return role_checker
