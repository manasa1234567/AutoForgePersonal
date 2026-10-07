from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from typing import Optional

# Dummy auth dependency placeholder
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="https://login.microsoftonline.com/common/oauth2/v2.0/authorize", tokenUrl="https://login.microsoftonline.com/common/oauth2/v2.0/token")

class User:
    def __init__(self, username: str, roles: Optional[list[str]] = None):
        self.username = username
        self.roles = roles or []

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # TODO: Integrate Microsoft Entra ID / Azure AD token validation and decode here
    # Simulated user for example:
    # A realistic implementation will verify token and fetch user and roles from the token claims

    # Here, we'll simulate with a hardcoded user
    # In actual usage, if authentication fails, raise HTTPException 401
    if token == "employee_token":
        return User(username="employee1", roles=["Employee"])
    elif token == "trainer_token":
        return User(username="trainer1", roles=["Trainer"])
    elif token == "manager_token":
        return User(username="manager1", roles=["Manager"])
    elif token == "coordinator_token":
        return User(username="coordinator1", roles=["Coordinator"])
    elif token == "admin_token":
        return User(username="admin1", roles=["Administrator"])
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_role(required_roles: list[str]):
    def role_dependency(user: User = Depends(get_current_user)):
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient permissions"
            )
        return user
    return role_dependency
