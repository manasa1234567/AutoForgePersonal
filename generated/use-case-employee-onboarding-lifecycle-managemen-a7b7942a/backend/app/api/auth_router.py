from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2AuthorizationCodeBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os
from jose import jwt, JWTError

# Configure OpenID Connect issuer and client info via environment variables
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "https://login.microsoftonline.com/common/v2.0")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
# For demo, no client secret needed; real apps need secret securely stored

# Endpoint for OAuth2 Authorization Code flow token retrieval (placeholder for doc/redirect)
# This is only used by frontend in real scenario

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{OIDC_ISSUER}/oauth2/v2.0/authorize",
    tokenUrl=f"{OIDC_ISSUER}/oauth2/v2.0/token",
    scopes={"openid": "OpenID Connect scope"},
)

router = APIRouter()

class User(BaseModel):
    username: str
    email: EmailStr
    roles: list[str]
    name: Optional[str] = None

    @property
    def is_hr_admin(self) -> bool:
        return "HR_ADMIN" in self.roles

    @property
    def is_hiring_manager(self) -> bool:
        return "HIRING_MANAGER" in self.roles

    @property
    def is_it_admin(self) -> bool:
        return "IT_ADMIN" in self.roles

    def can_access_employee(self, employee_id: int) -> bool:
        # For production, check user's allowed employee scopes or assignment
        # Here simplified: HR_ADMIN can access all, others restricted
        if self.is_hr_admin:
            return True
        if self.is_hiring_manager:
            # TODO: Implement logic for assigned employees
            return True
        if self.is_it_admin:
            return True
        # Normal employees only access themselves (not implemented fully here)
        return False

# For a true OpenID Connect integration, we must fetch and cache JWKS keys
_jwks_uri = f"{OIDC_ISSUER}/discovery/v2.0/keys"
_cached_jwks = None

async def get_jwks():
    global _cached_jwks
    if _cached_jwks is None:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(_jwks_uri)
            resp.raise_for_status()
            _cached_jwks = resp.json()
    return _cached_jwks

async def verify_token(token: str) -> dict:
    jwks = await get_jwks()
    # Identify the key based on token's kid
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token header")

    kid = unverified_header.get("kid")
    key = None
    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid:
            key = jwk
            break
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token kid")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=OIDC_CLIENT_ID,
            issuer=OIDC_ISSUER
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")
    return payload

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Validate JWT token using JWKS and decode claims
    payload = await verify_token(token)
    # Extract user info from claims
    preferred_username = payload.get("preferred_username") or payload.get("upn") or payload.get("email")
    email = payload.get("email")
    name = payload.get("name")
    # Extract roles from claims, for demo accept roles claim or groups claim
    roles = []
    if "roles" in payload and isinstance(payload["roles"], list):
        roles = payload["roles"]
    elif "groups" in payload and isinstance(payload["groups"], list):
        # Map groups to roles example
        groups = payload["groups"]
        # Map demo group-semantics to roles
        if "some-hr-group-id" in groups:
            roles.append("HR_ADMIN")
        if "some-manager-group-id" in groups:
            roles.append("HIRING_MANAGER")
        if "some-it-group-id" in groups:
            roles.append("IT_ADMIN")

    if not preferred_username or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = User(username=preferred_username, email=email, roles=roles, name=name)
    return user

# Token endpoint placeholder, in real scenario token is obtained by frontend via OAuth flow
@router.post("/token")
async def token():
    # Not implemented since real token comes from OpenID Connect Provider
    return {"detail": "Token issuance via OpenID Connect provider is handled externally."}

@router.get("/me", response_model=User)
async def current_user(user: User = Depends(get_current_user)):
    return user
