from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    full_name: Optional[str]
    email: Optional[str]
    roles: List[str]

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    disabled: Optional[bool]

    class Config:
        orm_mode = True
