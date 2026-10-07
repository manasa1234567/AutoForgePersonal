from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from app.models import UserBase
from typing import Optional

# Dummy OAuth2 scheme placeholder
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://login.microsoftonline.com/common/oauth2/authorize",
    tokenUrl="https://login.microsoftonline.com/common/oauth2/token"
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    # Dummy user for demonstration - actual implementation should validate token and retrieve user info from Azure AD
    # Here we simulate a decoded token payload
    if token == "fake-supertoken-for-admin":
        return UserBase(id=1, name="Admin User", email="admin@example.com", role="administrator")
    elif token == "fake-supertoken-for-manager":
        return UserBase(id=2, name="Manager User", email="manager@example.com", role="manager")
    elif token == "fake-supertoken-for-employee":
        return UserBase(id=3, name="Employee User", email="employee@example.com", role="employee")
    elif token == "fake-supertoken-for-trainer":
        return UserBase(id=4, name="Trainer User", email="trainer@example.com", role="trainer")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def get_user_role(user: UserBase = Depends(get_current_user)) -> str:
    return user.role
