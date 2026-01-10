"""
Интеграционные тесты для File Storage Service
Тестируют полные сценарии взаимодействия пользователей с системой
"""
import pytest
import io


class TestUserWorkflow:
    """Тестирует полный рабочий процесс пользователя"""

    def test_complete_user_journey(self, client):
        """
        Полный путь пользователя:
        1. Регистрация
        2. Вход
        3. Загрузка файла
        4. Просмотр списка файлов
        5. Скачивание файла
        6. Удаление файла
        """
        # 1. Регистрация
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "journey@example.com",
                "password": "JourneyPass123!",
            },
        )
        assert register_response.status_code == 200
        user_data = register_response.json()
        assert "id" in user_data

        # 2. Вход
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "journey@example.com",
                "password": "JourneyPass123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Загрузка файла
        file_content = b"Test file content for integration test"
        file = io.BytesIO(file_content)
        upload_response = client.post(
            "/api/v1/files/upload",
            files={"file": ("integration_test.txt", file, "text/plain")},
            headers=headers,
        )
        assert upload_response.status_code == 200
        uploaded_file = upload_response.json()
        file_id = uploaded_file["id"]
        assert uploaded_file["filename"] == "integration_test.txt"

        # 4. Просмотр списка файлов
        list_response = client.get("/api/v1/files/", headers=headers)
        assert list_response.status_code == 200
        files_list = list_response.json()
        assert len(files_list) >= 1
        assert any(f["id"] == file_id for f in files_list)

        # 5. Скачивание файла
        download_response = client.get(
            f"/api/v1/files/{file_id}/download",
            headers=headers,
        )
        assert download_response.status_code == 200
        assert len(download_response.content) > 0

        # 6. Удаление файла
        delete_response = client.delete(
            f"/api/v1/files/{file_id}",
            headers=headers,
        )
        assert delete_response.status_code == 200

        # Проверка что файл удалён
        list_after_delete = client.get("/api/v1/files/", headers=headers)
        files_after = list_after_delete.json()
        assert not any(f["id"] == file_id for f in files_after)


class TestMultiUserInteraction:
    """Тестирует взаимодействие нескольких пользователей"""

    def test_file_isolation_between_users(self, client):
        """
        Проверяет что пользователи видят только свои файлы
        """
        # Создать двух пользователей
        # Пользователь 1
        client.post(
            "/api/v1/auth/register",
            json={"email": "user1@example.com", "password": "User1Pass123!"},
        )
        login1 = client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "User1Pass123!"},
        )
        token1 = login1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Пользователь 2
        client.post(
            "/api/v1/auth/register",
            json={"email": "user2@example.com", "password": "User2Pass123!"},
        )
        login2 = client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "User2Pass123!"},
        )
        token2 = login2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User1 загружает файл
        file1 = io.BytesIO(b"User1 file content")
        upload1 = client.post(
            "/api/v1/files/upload",
            files={"file": ("user1_file.txt", file1, "text/plain")},
            headers=headers1,
        )
        assert upload1.status_code == 200
        file1_id = upload1.json()["id"]

        # User2 загружает файл
        file2 = io.BytesIO(b"User2 file content")
        upload2 = client.post(
            "/api/v1/files/upload",
            files={"file": ("user2_file.txt", file2, "text/plain")},
            headers=headers2,
        )
        assert upload2.status_code == 200
        file2_id = upload2.json()["id"]

        # User1 должен видеть только свой файл
        user1_files = client.get("/api/v1/files/", headers=headers1).json()
        user1_file_ids = [f["id"] for f in user1_files]
        assert file1_id in user1_file_ids
        assert file2_id not in user1_file_ids

        # User2 должен видеть только свой файл
        user2_files = client.get("/api/v1/files/", headers=headers2).json()
        user2_file_ids = [f["id"] for f in user2_files]
        assert file2_id in user2_file_ids
        assert file1_id not in user2_file_ids

        # User1 не может скачать файл User2
        download_attempt = client.get(
            f"/api/v1/files/{file2_id}/download",
            headers=headers1,
        )
        assert download_attempt.status_code in [403, 404]

        # User2 не может удалить файл User1
        delete_attempt = client.delete(
            f"/api/v1/files/{file1_id}",
            headers=headers2,
        )
        assert delete_attempt.status_code in [403, 404]

    def test_multiple_file_uploads(self, client, user_token):
        """
        Тест загрузки нескольких файлов одним пользователем
        """
        headers = {"Authorization": f"Bearer {user_token}"}
        file_ids = []

        # Загрузить несколько файлов
        for i in range(5):
            file = io.BytesIO(f"File {i} content".encode())
            response = client.post(
                "/api/v1/files/upload",
                files={"file": (f"file_{i}.txt", file, "text/plain")},
                headers=headers,
            )
            assert response.status_code == 200
            file_ids.append(response.json()["id"])

        # Проверить что все файлы в списке
        files_list = client.get("/api/v1/files/", headers=headers).json()
        list_ids = [f["id"] for f in files_list]

        for file_id in file_ids:
            assert file_id in list_ids


class TestFileOperations:
    """Тестирует различные операции с файлами"""

    def test_upload_different_file_types(self, client, user_token):
        """
        Тест загрузки файлов разных типов
        """
        headers = {"Authorization": f"Bearer {user_token}"}

        file_types = [
            ("test.txt", b"Text content", "text/plain"),
            ("test.pdf", b"%PDF-1.4 fake pdf", "application/pdf"),
            ("test.json", b'{"key": "value"}', "application/json"),
            ("test.csv", b"a,b,c\n1,2,3", "text/csv"),
        ]

        for filename, content, mimetype in file_types:
            file = io.BytesIO(content)
            response = client.post(
                "/api/v1/files/upload",
                files={"file": (filename, file, mimetype)},
                headers=headers,
            )
            assert response.status_code == 200, f"Failed to upload {filename}"
            uploaded = response.json()
            assert uploaded["filename"] == filename
            # Проверяем что файл загружен, но тип может не возвращаться в response
            assert "id" in uploaded

    def test_file_size_tracking(self, client, user_token):
        """
        Тест корректного отслеживания размера файлов
        """
        headers = {"Authorization": f"Bearer {user_token}"}

        # Создать файл известного размера
        file_size = 1024  # 1 KB
        content = b"A" * file_size
        file = io.BytesIO(content)

        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("size_test.txt", file, "text/plain")},
            headers=headers,
        )
        assert response.status_code == 200
        uploaded = response.json()
        assert uploaded["size"] == file_size


class TestAuthenticationFlow:
    """Тестирует различные сценарии аутентификации"""

    def test_token_expiration_behavior(self, client):
        """
        Тест поведения системы с токенами
        """
        # Регистрация и вход
        client.post(
            "/api/v1/auth/register",
            json={"email": "token_test@example.com", "password": "TokenTest123!"},
        )
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "token_test@example.com", "password": "TokenTest123!"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        # Использование токена для доступа
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/files/", headers=headers)
        assert response.status_code == 200

        # Попытка доступа с неверным токеном
        bad_headers = {"Authorization": "Bearer invalid_token_12345"}
        bad_response = client.get("/api/v1/files/", headers=bad_headers)
        assert bad_response.status_code in [401, 422]

        # Попытка доступа без токена
        no_token_response = client.get("/api/v1/files/")
        assert no_token_response.status_code in [401, 403]

    def test_concurrent_logins(self, client):
        """
        Тест множественных входов одного пользователя
        """
        email = "concurrent@example.com"
        password = "ConcurrentPass123!"

        # Регистрация
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )

        # Несколько входов
        tokens = []
        for _ in range(3):
            login = client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password},
            )
            assert login.status_code == 200
            tokens.append(login.json()["access_token"])

        # Все токены должны работать
        for token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/files/", headers=headers)
            assert response.status_code == 200


class TestErrorHandling:
    """Тестирует обработку ошибок"""

    def test_upload_without_file(self, client, user_token):
        """
        Тест загрузки без файла
        """
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post("/api/v1/files/upload", headers=headers)
        assert response.status_code == 422  # Validation error

    def test_download_nonexistent_file(self, client, user_token):
        """
        Тест скачивания несуществующего файла
        """
        headers = {"Authorization": f"Bearer {user_token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/files/{fake_id}/download",
            headers=headers,
        )
        assert response.status_code == 404

    def test_delete_nonexistent_file(self, client, user_token):
        """
        Тест удаления несуществующего файла
        """
        headers = {"Authorization": f"Bearer {user_token}"}
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(f"/api/v1/files/{fake_id}", headers=headers)
        assert response.status_code == 404
