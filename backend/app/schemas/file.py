from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.schemas.base import BaseModel
import uuid

class File(BaseModel):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Информация о файле
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), unique=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)

    # Организация
    folder = Column(String(100), default="root", nullable=False)
    tags = Column(Text, nullable=True)

    # Безопасность
    file_hash = Column(String(64), nullable=False)
    is_deleted = Column(Boolean, default=False, index=True)

    # Хранилище
    s3_path = Column(String(500), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="files")
