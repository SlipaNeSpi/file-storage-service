import io
import pytest


def test_upload_file(client, user_token):
    """Тест загрузки файла"""
    file_content = b"Test file content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert "id" in data


def test_upload_file_unauthorized(client):
    """Тест загрузки файла без авторизации"""
    file = io.BytesIO(b"content")
    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", file, "text/plain")},
    )
    assert response.status_code in [401, 403]


def test_list_files(client, user_token):
    """Тест получения списка файлов"""
    # Сначала загрузим файл
    file = io.BytesIO(b"Test content")
    client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Теперь получим список
    response = client.get(
        "/api/v1/files/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_file(client, user_token):
    """Тест удаления файла"""
    # Загрузим файл
    file = io.BytesIO(b"Test content")
    upload_response = client.post(
        "/api/v1/files/upload",
        files={"file": ("test.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    file_id = upload_response.json()["id"]

    # Удалим файл
    response = client.delete(
        f"/api/v1/files/{file_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200


def test_delete_other_user_file(client, user_token, admin_token):
    """Тест: обычный пользователь не может удалить чужой файл"""
    # Админ загружает файл
    file = io.BytesIO(b"Admin file")
    upload_response = client.post(
        "/api/v1/files/upload",
        files={"file": ("admin.txt", file, "text/plain")},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    file_id = upload_response.json()["id"]

    # Обычный пользователь пытается удалить
    response = client.delete(
        f"/api/v1/files/{file_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    # API возвращает 404 чтобы скрыть существование файла
    assert response.status_code in [403, 404]
