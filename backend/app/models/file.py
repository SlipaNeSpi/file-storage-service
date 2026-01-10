from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "document.pdf",
                "size": 1024000,
                "created_at": "2026-01-08T18:00:00"
            }
        }

class FileMetadata(BaseModel):
    id: str
    filename: str
    size: int
    type: str
    hash: str
    created_at: datetime
    updated_at: datetime

class FileListItem(BaseModel):
    id: str
    filename: str
    size: int
    type: str
    folder: str
    created_at: datetime

    class Config:
        from_attributes = True
