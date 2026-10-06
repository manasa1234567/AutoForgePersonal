from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    email: str
    roles: List[str]

class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    roles: Optional[List[str]]
