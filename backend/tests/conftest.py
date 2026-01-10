import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import get_settings

settings = get_settings()

# Используем отдельную тестовую БД PostgreSQL
# Если DATABASE_URL = "postgresql://user:pass@localhost/file_storage"
# То для тестов используем "postgresql://user:pass@localhost/file_storage_test"
TEST_DATABASE_URL = settings.DATABASE_URL.rsplit('/', 1)[0] + '/file_storage_test'

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Создаёт тестовую БД один раз перед всеми тестами"""
    Base.metadata.create_all(bind=engine)
    yield
    # После всех тестов можно очистить
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Создаёт сессию БД для каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Создаёт тестовый клиент FastAPI"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    """Создаёт тестового пользователя через API"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200, f"Registration failed: {response.text}"
    return response.json()


@pytest.fixture
def test_admin(client):
    """Создаёт тестового админа через API"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "Admin123!",
        },
    )
    assert response.status_code == 200, f"Registration failed: {response.text}"
    return response.json()


@pytest.fixture
def user_token(client, test_user):
    """Получает токен для тестового пользователя"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin):
    """Получает токен для админа"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "Admin123!",
        },
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]
