from sqlalchemy.orm import Session
from app.schemas.file import File
from app.repositories.file_repository import FileRepository
from app.services.storage_service import StorageService
from app.models.file import FileUploadResponse
from fastapi import UploadFile
from app.config import get_settings
import uuid

settings = get_settings()


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.file_repo = FileRepository(db)
        self.storage = StorageService()

    async def upload_file(
            self,
            user_id: str,
            file: UploadFile,
            folder: str = "root"
    ) -> FileUploadResponse:
        """Загрузка одного файла"""
        # Проверка размера
        file_data = await file.read()
        if len(file_data) > settings.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Max size: {settings.MAX_FILE_SIZE / 1e9} GB")

        # Проверка расширения
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ""
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}")

        # Загрузка в MinIO
        storage_info = await self.storage.upload_file(
            user_id,
            file.filename or "unknown",
            file_data
        )

        # Сохранение в БД
        new_file = self.file_repo.create({
            "owner_id": uuid.UUID(user_id),
            "original_name": file.filename or "unknown",
            "stored_name": storage_info['stored_name'],
            "file_size": storage_info['size'],
            "file_type": file.content_type or 'application/octet-stream',
            "folder": folder,
            "file_hash": storage_info['file_hash'],
            "s3_path": f"s3://{settings.MINIO_BUCKET_NAME}/{storage_info['stored_name']}"
        })

        return FileUploadResponse(
            id=str(new_file.id),
            filename=new_file.original_name,
            size=new_file.file_size,
            created_at=new_file.created_at
        )

    async def download_file(self, file_id: str, user_id: str) -> tuple[bytes, str]:
        """Скачивание файла"""
        file = self.file_repo.get_by_id(file_id)

        if not file or str(file.owner_id) != user_id:
            raise ValueError("File not found or access denied")

        file_data = await self.storage.download_file(file.stored_name)
        return file_data, file.original_name

    async def delete_file(self, file_id: str, user_id: str):
        """Удаление файла"""
        file = self.file_repo.get_by_id(file_id)

        if not file or str(file.owner_id) != user_id:
            raise ValueError("File not found or access denied")

        await self.storage.delete_file(file.stored_name)
        self.file_repo.soft_delete(file_id)

        return {"message": "File deleted successfully"}

    async def rename_file(self, file_id: str, new_name: str, user_id: str):
        """Переименование файла"""
        file = self.file_repo.get_by_id(file_id)

        if not file or str(file.owner_id) != user_id:
            raise ValueError("File not found or access denied")

        self.file_repo.update_name(file_id, new_name)

        return {"filename": new_name}

    def get_user_files(
            self,
            user_id: str,
            folder: str = "root",
            skip: int = 0,
            limit: int = 20
    ):
        """Получение списка файлов пользователя"""
        files = self.file_repo.get_user_files(user_id, folder, skip, limit)

        # Возвращаем список словарей
        return [
            {
                "id": str(f.id),
                "filename": f.original_name,
                "size": f.file_size,
                "type": f.file_type,
                "folder": f.folder,
                "created_at": f.created_at.isoformat()
            }
            for f in files
        ]

    def get_file_metadata(self, file_id: str, user_id: str):
        """Получение метаданных файла"""
        file = self.file_repo.get_by_id(file_id)

        if not file or str(file.owner_id) != user_id:
            raise ValueError("File not found or access denied")

        return {
            "id": str(file.id),
            "filename": file.original_name,
            "size": file.file_size,
            "type": file.file_type,
            "hash": file.file_hash,
            "created_at": file.created_at.isoformat(),
            "updated_at": file.updated_at.isoformat()
        }
