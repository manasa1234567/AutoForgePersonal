from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.status import HTTP_401_UNAUTHORIZED
from typing import Optional
from app.core.config import settings
from app.models.user import UserBase, UserRole

router = APIRouter()

# Assume Azure AD OAuth2 endpoints
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{settings.AZURE_AD_TENANT_ID}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{settings.AZURE_AD_TENANT_ID}/oauth2/v2.0/token"
)

async def verify_token(token: str = Depends(oauth2_scheme)) -> UserBase:
    # Simplified token validation stub
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    # In real app, validate token via Microsoft and extract user info
    # Here, mock user
    return UserBase(
        id=1,
        username="johndoe",
        email="john.doe@example.com",
        full_name="John Doe",
        role=UserRole.employee,
        is_active=True,
        date_joined=None,
    )

async def verify_admin(user: UserBase = Depends(verify_token)):
    if user.role != UserRole.administrator:
        raise HTTPException(status_code=403, detail="Access denied: administrator only")
    return user

@router.get("/me", response_model=UserBase)
async def read_current_user(user: UserBase = Depends(verify_token)):
    return user
