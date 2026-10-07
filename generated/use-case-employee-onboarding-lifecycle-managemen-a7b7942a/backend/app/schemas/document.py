from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentRead(BaseModel):
    document_id: int
    employee_id: int
    document_name: str
    upload_date: datetime
    file_url: str

    class Config:
        orm_mode = True

class DocumentCreate(BaseModel):
    employee_id: int
    document_name: str
    file_url: str
