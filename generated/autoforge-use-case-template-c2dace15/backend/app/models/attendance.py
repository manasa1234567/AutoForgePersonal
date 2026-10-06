from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    session_id: int
    employee_id: int
    present: bool

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    marked_at: datetime

    class Config:
        orm_mode = True
