from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional

# Dummy OAuth2 scheme for demonstration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

class User(BaseModel):
    username: str
    email: EmailStr
    roles: list[str]

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
        # Simplified - HR admins can access all, hiring managers can access assigned employees
        if self.is_hr_admin:
            return True
        if self.is_hiring_manager:
            # TODO: In real app check assignments
            return True
        if self.is_it_admin:
            # IT Admins read only during onboarding?
            return True
        # Normal employees only access themselves?
        return False

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Dummy user for demo
    if token == "hr_token":
        return User(username="hruser", email="hr@example.com", roles=["HR_ADMIN"])
    elif token == "manager_token":
        return User(username="manageruser", email="manager@example.com", roles=["HIRING_MANAGER"])
    elif token == "it_token":
        return User(username="ituser", email="it@example.com", roles=["IT_ADMIN"])
    elif token == "employee_token":
        return User(username="employeeuser", email="emp@example.com", roles=["EMPLOYEE"])
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

@router.post("/token")
async def login():
    return {"access_token": "hr_token", "token_type": "bearer"}

@router.get("/me", response_model=User)
async def current_user(user: User = Depends(get_current_user)):
    return user
