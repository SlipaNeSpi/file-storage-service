from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.schemas.file import File
from uuid import UUID
from typing import Optional, List

class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, file_id: str) -> Optional[File]:

        return self.db.query(File).filter(
            and_(File.id == UUID(file_id), File.is_deleted == False)
        ).first()

    def get_user_files(
        self,
        user_id: str,
        folder: str = "root",
        skip: int = 0,
        limit: int = 20
    ) -> List[File]:

        return self.db.query(File).filter(
            and_(
                File.owner_id == UUID(user_id),
                File.folder == folder,
                File.is_deleted == False
            )
        ).offset(skip).limit(limit).all()

    def create(self, file_data: dict) -> File:
        """Создать запись о файле"""
        file = File(**file_data)
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    def soft_delete(self, file_id: str):
        """Мягкое удаление файла"""
        file = self.get_by_id(file_id)
        if file:
            file.is_deleted = True
            self.db.commit()

    def update_name(self, file_id: str, new_name: str):
        """Обновить имя файла"""
        file = self.get_by_id(file_id)
        if file:
            file.original_name = new_name
            self.db.commit()
