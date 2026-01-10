from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.base import BaseModel
from enum import Enum as PyEnum
import uuid

class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String, default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    last_login = Column(DateTime, nullable=True)

    files = relationship("File", back_populates="owner")

    # временно без связей, чтобы не было циклов
