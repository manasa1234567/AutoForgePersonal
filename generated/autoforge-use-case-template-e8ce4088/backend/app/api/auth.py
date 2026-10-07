from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from fastapi import Request
import httpx
import time

# Configuration for Azure AD
AZURE_AD_TENANT = "common"  # or your tenant ID
AZURE_AD_CLIENT_ID = "your-client-id"
AZURE_AD_ISSUER = f"https://login.microsoftonline.com/{AZURE_AD_TENANT}/v2.0"
JWKS_URL = f"https://login.microsoftonline.com/{AZURE_AD_TENANT}/discovery/v2.0/keys"

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://login.microsoftonline.com/{AZURE_AD_TENANT}/oauth2/v2.0/authorize",
    tokenUrl=f"https://login.microsoftonline.com/{AZURE_AD_TENANT}/oauth2/v2.0/token",
    scopes={},
)

class User(BaseModel):
    username: str
    roles: list[str] = []

# Cache JWKS (JSON Web Key Set) for signature verification
_jwks_cache = None
_jwks_cache_time = 0

async def get_jwks():
    global _jwks_cache, _jwks_cache_time
    now = time.time()
    if _jwks_cache and now - _jwks_cache_time < 3600:  # 1 hour cache
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_cache_time = now
        return _jwks_cache

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        key = None
        for jwk in jwks["keys"]:
            if jwk["kid"] == kid:
                key = jwk
                break
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

        payload = jwt.decode(
            token,
            key,
            algorithms=[unverified_header.get("alg", "RS256")],
            audience=AZURE_AD_CLIENT_ID,
            issuer=AZURE_AD_ISSUER,
        )
        username: str = payload.get("preferred_username") or payload.get("upn") or payload.get("email")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
        roles = payload.get("roles", [])
        if isinstance(roles, str):
            roles = [roles]
        user = User(username=username, roles=roles)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info"""
    return current_user
