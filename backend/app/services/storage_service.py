from minio import Minio
from minio.error import S3Error
from app.config import get_settings
import io
import hashlib
import uuid

settings = get_settings()

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_URL.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Создание bucket если его нет"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✓ Bucket '{self.bucket_name}' created")
        except S3Error as e:
            print(f"Warning: Could not ensure bucket exists: {e}")

    async def upload_file(
        self,
        user_id: str,
        filename: str,
        file_data: bytes
    ) -> dict:
        """Загрузка файла в MinIO"""
        try:
            # Генерация уникального имени
            unique_name = str(uuid.uuid4())
            stored_name = f"{user_id}/{unique_name}"

            # Вычисление хеша
            file_hash = hashlib.sha256(file_data).hexdigest()

            # Загрузка в MinIO
            self.client.put_object(
                self.bucket_name,
                stored_name,
                io.BytesIO(file_data),
                len(file_data),
                content_type="application/octet-stream"
            )

            return {
                "stored_name": stored_name,
                "file_hash": file_hash,
                "size": len(file_data)
            }
        except S3Error as e:
            raise Exception(f"Upload failed: {e}")

    async def download_file(self, stored_name: str) -> bytes:
        """Скачивание файла"""
        try:
            response = self.client.get_object(self.bucket_name, stored_name)
            return response.read()
        except S3Error as e:
            raise Exception(f"Download failed: {e}")

    async def delete_file(self, stored_name: str):
        """Удаление файла"""
        try:
            self.client.remove_object(self.bucket_name, stored_name)
        except S3Error as e:
            raise Exception(f"Delete failed: {e}")
