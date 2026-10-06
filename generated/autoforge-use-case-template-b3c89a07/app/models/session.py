from pydantic import BaseModel

class SessionInfo(BaseModel):
    session_id: int
    program_name: str
    course_name: str
    date: str  # ISO format
    capacity: int
    registered_count: int
    status: str  # e.g., "Scheduled", "Completed", "Cancelled"

class SessionRegistrationRequest(BaseModel):
    session_id: int

