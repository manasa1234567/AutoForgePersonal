from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import SecurityScopes
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

# Dummy secret and algorithm for JWT (should be environment variable in prod)
SECRET_KEY = "supersecretkeychangeme"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Roles
ROLES = ["employee", "trainer", "manager", "coordinator", "admin"]

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: Optional[list[str]] = []

class User(BaseModel):
    username: str
    roles: list[str]
    disabled: Optional[bool] = False

# Fake user db for demo
fake_users_db = {
    "alice": {"username": "alice", "hashed_password": "fakehashedsecret", "roles": ["employee"], "disabled": False},
    "bob": {"username": "bob", "hashed_password": "fakehashedsecret", "roles": ["trainer"], "disabled": False},
    "carol": {"username": "carol", "hashed_password": "fakehashedsecret", "roles": ["manager"], "disabled": False},
    "dan": {"username": "dan", "hashed_password": "fakehashedsecret", "roles": ["coordinator"], "disabled": False},
    "admin": {"username": "admin", "hashed_password": "fakehashedsecret", "roles": ["admin"], "disabled": False},
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # For demonstration assume plain password match
    return plain_password == "secret" and hashed_password == "fakehashedsecret"

def get_user(db, username: str) -> User | None:
    if username in db:
        user_dict = db[username]
        return User(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user:
        return None
    if not verify_password(password, fake_users_db[username]["hashed_password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        roles: list[str] = payload.get("roles", [])
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, roles=roles)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_roles(allowed_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not any(role in allowed_roles for role in current_user.roles):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user
    return role_checker
