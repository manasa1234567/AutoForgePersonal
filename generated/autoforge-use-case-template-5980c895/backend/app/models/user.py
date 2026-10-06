from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.core.db import Base
import enum

class UserRole(str, enum.Enum):
    EMPLOYEE = "Employee"
    TRAINER = "Trainer"
    MANAGER = "Manager"
    ADMIN = "Administrator"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
