from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    full_name: Optional[str]
    email: Optional[str]
    roles: List[str]

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    disabled: Optional[bool] = False

    class Config:
        orm_mode = True
