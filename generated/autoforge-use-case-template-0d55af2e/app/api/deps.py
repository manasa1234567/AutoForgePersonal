from fastapi import Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from app.api.api_v1.endpoints.auth import verify_token

async def verify_token_optional(token: str = None):
    # Placeholder for optional auth
    if not token:
        return None
    return await verify_token(token)

async def verify_token(user=Depends(verify_token)):
    return user

async def verify_admin(user=Depends(verify_token)):
    if user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    return user
