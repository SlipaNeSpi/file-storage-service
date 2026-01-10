from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "File Storage Service"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:123@localhost:5432/file_storage"

    SECRET_KEY: str = "your-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    MINIO_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "files"

    REDIS_URL: str = "redis://localhost:6379"

    MAX_FILE_SIZE: int = 1_000_000_000  # 1 GB
    ALLOWED_EXTENSIONS: set[str] = {
        "pdf", "doc", "docx", "xls", "xlsx",
        "jpg", "jpeg", "png", "gif", "webp",
        "mp4", "avi", "mov",
        "zip", "rar", "7z",
        "txt", "csv", "json", "xml"
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()

if __name__ == "__main__":
    s = get_settings()
    print(f"DATABASE_URL: {s.DATABASE_URL}")