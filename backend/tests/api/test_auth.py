import pytest


def test_health_check(client):
    """Тест health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_user(client):
    """Тест регистрации нового пользователя"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "NewPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_register_duplicate_email(client, test_user):
    """Тест регистрации с существующим email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Pass123!",
        },
    )
    assert response.status_code == 400 or response.status_code == 422


def test_login_success(client, test_user):
    """Тест успешного входа"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Тест входа с неверным паролем"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPass123!",
        },
    )
    assert response.status_code == 400 or response.status_code == 401


def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "Pass123!",
        },
    )
    assert response.status_code == 400 or response.status_code == 401
