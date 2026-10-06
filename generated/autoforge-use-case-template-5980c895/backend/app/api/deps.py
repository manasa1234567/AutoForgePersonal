from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_role(current_user: User, allowed_roles: list[str]) -> User:
    if current_user.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

async def get_current_active_trainer(current_user: User = Depends(get_current_active_user)) -> User:
    return await check_role(current_user, [UserRole.TRAINER, UserRole.ADMIN])

async def get_current_active_manager(current_user: User = Depends(get_current_active_user)) -> User:
    return await check_role(current_user, [UserRole.MANAGER, UserRole.ADMIN])

async def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    return await check_role(current_user, [UserRole.ADMIN])
