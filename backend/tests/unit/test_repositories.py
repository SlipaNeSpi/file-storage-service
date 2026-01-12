"""
Unit tests for repository layer
Tests UserRepository and FileRepository functionality
"""
import pytest
from uuid import uuid4
from app.repositories.user_repository import UserRepository
from app.repositories.file_repository import FileRepository
from app.schemas.user import User
from app.schemas.file import File


class TestUserRepository:
    """Test suite for UserRepository"""

    def test_create_user(self, db):
        """Test creating a new user"""
        repo = UserRepository(db)
        
        user = repo.create(
            email="newuser@test.com",
            username="newuser",
            hashed_password="hashed_password_here"
        )
        
        assert user is not None
        assert user.id is not None
        assert user.email == "newuser@test.com"
        assert user.username == "newuser"
        assert user.role == "user"  # Default role
        assert user.is_active is True
        assert user.is_verified is False

    def test_get_by_email_existing(self, db):
        """Test retrieving user by email"""
        repo = UserRepository(db)
        
        # Create user
        created_user = repo.create(
            email="findme@test.com",
            username="findme",
            hashed_password="hashed_pass"
        )
        
        # Find user
        found_user = repo.get_by_email("findme@test.com")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "findme@test.com"

    def test_get_by_email_nonexistent(self, db):
        """Test retrieving non-existent user returns None"""
        repo = UserRepository(db)
        
        user = repo.get_by_email("nonexistent@test.com")
        
        assert user is None

    def test_get_by_username(self, db):
        """Test retrieving user by username"""
        repo = UserRepository(db)
        
        repo.create(
            email="user@test.com",
            username="testusername",
            hashed_password="hashed_pass"
        )
        
        found = repo.get_by_username("testusername")
        
        assert found is not None
        assert found.username == "testusername"

    def test_get_by_id(self, db):
        """Test retrieving user by ID"""
        repo = UserRepository(db)
        
        user = repo.create(
            email="idtest@test.com",
            username="idtest",
            hashed_password="hashed_pass"
        )
        
        found = repo.get_by_id(str(user.id))
        
        assert found is not None
        assert found.id == user.id
        assert found.email == user.email

    def test_get_all_with_pagination(self, db):
        """Test getting all users with pagination"""
        repo = UserRepository(db)
        
        # Create multiple users
        for i in range(5):
            repo.create(
                email=f"user{i}@test.com",
                username=f"user{i}",
                hashed_password="hashed_pass"
            )
        
        # Get first 3
        users_page1 = repo.get_all(skip=0, limit=3)
        assert len(users_page1) >= 3
        
        # Get next 2
        users_page2 = repo.get_all(skip=3, limit=2)
        assert len(users_page2) >= 2

    def test_update_last_login(self, db):
        """Test updating last login timestamp"""
        repo = UserRepository(db)
        
        user = repo.create(
            email="logintest@test.com",
            username="logintest",
            hashed_password="hashed_pass"
        )
        
        assert user.last_login is None
        
        # Update last login
        repo.update_last_login(str(user.id))
        
        # Verify update
        updated_user = repo.get_by_id(str(user.id))
        assert updated_user.last_login is not None


class TestFileRepository:
    """Test suite for FileRepository"""

    @pytest.fixture
    def test_user(self, db):
        """Create a test user for file tests"""
        repo = UserRepository(db)
        return repo.create(
            email="fileowner@test.com",
            username="fileowner",
            hashed_password="hashed_pass"
        )

    def test_create_file(self, db, test_user):
        """Test creating a file record"""
        repo = FileRepository(db)
        
        file_data = {
            "owner_id": test_user.id,
            "original_name": "test.pdf",
            "stored_name": f"{uuid4()}.pdf",
            "file_size": 1024,
            "file_type": "application/pdf",
            "folder": "Documents",
            "file_hash": "abc123hash",
            "s3_path": "/files/test.pdf"
        }
        
        file = repo.create(file_data)
        
        assert file is not None
        assert file.id is not None
        assert file.owner_id == test_user.id
        assert file.original_name == "test.pdf"
        assert file.file_size == 1024
        assert file.is_deleted is False

    def test_get_by_id(self, db, test_user):
        """Test retrieving file by ID"""
        repo = FileRepository(db)
        
        # Create file
        file_data = {
            "owner_id": test_user.id,
            "original_name": "find.txt",
            "stored_name": f"{uuid4()}.txt",
            "file_size": 512,
            "file_type": "text/plain",
            "folder": "root",
            "file_hash": "def456hash",
            "s3_path": "/files/find.txt"
        }
        created_file = repo.create(file_data)
        
        # Find file
        found = repo.get_by_id(str(created_file.id))
        
        assert found is not None
        assert found.id == created_file.id
        assert found.original_name == "find.txt"

    def test_get_user_files_filtered_by_folder(self, db, test_user):
        """Test getting user files filtered by folder"""
        repo = FileRepository(db)
        
        # Create files in different folders
        for i in range(3):
            repo.create({
                "owner_id": test_user.id,
                "original_name": f"doc{i}.txt",
                "stored_name": f"{uuid4()}.txt",
                "file_size": 100,
                "file_type": "text/plain",
                "folder": "Documents",
                "file_hash": f"hash{i}",
                "s3_path": f"/files/doc{i}.txt"
            })
        
        for i in range(2):
            repo.create({
                "owner_id": test_user.id,
                "original_name": f"pic{i}.jpg",
                "stored_name": f"{uuid4()}.jpg",
                "file_size": 200,
                "file_type": "image/jpeg",
                "folder": "Photos",
                "file_hash": f"hash{i}",
                "s3_path": f"/files/pic{i}.jpg"
            })
        
        # Get Documents folder files
        docs = repo.get_user_files(str(test_user.id), folder="Documents")
        assert len(docs) == 3
        assert all(f.folder == "Documents" for f in docs)
        
        # Get Photos folder files
        photos = repo.get_user_files(str(test_user.id), folder="Photos")
        assert len(photos) == 2
        assert all(f.folder == "Photos" for f in photos)

    def test_soft_delete_file(self, db, test_user):
        """Test soft deletion of file"""
        repo = FileRepository(db)
        
        # Create file
        file_data = {
            "owner_id": test_user.id,
            "original_name": "delete_me.txt",
            "stored_name": f"{uuid4()}.txt",
            "file_size": 100,
            "file_type": "text/plain",
            "folder": "root",
            "file_hash": "deletehash",
            "s3_path": "/files/delete_me.txt"
        }
        file = repo.create(file_data)
        assert file.is_deleted is False
        
        # Soft delete
        repo.soft_delete(str(file.id))
        
        # File should not be found (soft deleted)
        found = repo.get_by_id(str(file.id))
        assert found is None  # get_by_id filters out deleted files

    def test_update_file_name(self, db, test_user):
        """Test updating file name"""
        repo = FileRepository(db)
        
        # Create file
        file_data = {
            "owner_id": test_user.id,
            "original_name": "old_name.txt",
            "stored_name": f"{uuid4()}.txt",
            "file_size": 100,
            "file_type": "text/plain",
            "folder": "root",
            "file_hash": "renamehash",
            "s3_path": "/files/old_name.txt"
        }
        file = repo.create(file_data)
        
        # Update name
        repo.update_name(str(file.id), "new_name.txt")
        
        # Verify update
        updated = repo.get_by_id(str(file.id))
        assert updated.original_name == "new_name.txt"

    def test_pagination_in_get_user_files(self, db, test_user):
        """Test pagination when getting user files"""
        repo = FileRepository(db)
        
        # Create 10 files
        for i in range(10):
            repo.create({
                "owner_id": test_user.id,
                "original_name": f"file{i}.txt",
                "stored_name": f"{uuid4()}.txt",
                "file_size": 100,
                "file_type": "text/plain",
                "folder": "root",
                "file_hash": f"hash{i}",
                "s3_path": f"/files/file{i}.txt"
            })
        
        # Get first page (5 files)
        page1 = repo.get_user_files(str(test_user.id), skip=0, limit=5)
        assert len(page1) == 5
        
        # Get second page (5 files)
        page2 = repo.get_user_files(str(test_user.id), skip=5, limit=5)
        assert len(page2) == 5
        
        # Ensure different files
        page1_ids = {str(f.id) for f in page1}
        page2_ids = {str(f.id) for f in page2}
        assert page1_ids.isdisjoint(page2_ids)
