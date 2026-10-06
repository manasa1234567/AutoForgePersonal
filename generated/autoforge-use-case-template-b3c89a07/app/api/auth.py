from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel
from typing import Optional

# Simplified OAuth2 for Microsoft Entra ID (Azure AD) integration
# In a real system, use MSAL and validate tokens properly

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    scopes={"openid": "Sign in"}
)

class Token(BaseModel):
    access_token: str
    token_type: str

# Fake in-memory session store (to be replaced by real OAuth2 verifier)
active_sessions = {}

@router.get("/userinfo")
async def user_info(token: str = Depends(oauth2_scheme)):
    # Validate and decode token with Azure AD (stubbed)
    # For demo, accept any token, return dummy user info
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # Dummy user info
    user = {
        "sub": "user123",
        "name": "Jane Employee",
        "preferred_username": "jane.employee@company.com",
        "roles": ["employee"]
    }
    return user
