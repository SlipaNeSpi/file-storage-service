"""
Unit tests for AuthService
Tests registration, login, and authentication logic
"""
import pytest
from app.services.auth_service import AuthService
from app.models.auth import UserRegister, UserLogin
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import PasswordUtils


class TestAuthService:
    """Test suite for AuthService"""

    @pytest.mark.asyncio
    async def test_register_success(self, db):
        """Test successful user registration"""
        auth_service = AuthService(db)
        
        user_data = UserRegister(
            email="newuser@example.com",
            password="SecurePass123!"
        )
        
        result = await auth_service.register(user_data)
        
        assert "id" in result
        assert result["email"] == "newuser@example.com"
        assert "message" in result
        assert "registered successfully" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db):
        """Test registration with already existing email"""
        auth_service = AuthService(db)
        
        # Register first user
        user_data = UserRegister(
            email="duplicate@example.com",
            password="SecurePass123!"
        )
        await auth_service.register(user_data)
        
        # Try to register again with same email
        with pytest.raises(ValueError, match="already exists"):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, db):
        """Test registration with invalid email format"""
        auth_service = AuthService(db)
        
        user_data = UserRegister(
            email="invalid-email",
            password="SecurePass123!"
        )
        
        with pytest.raises(ValueError, match="Invalid email"):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_weak_password(self, db):
        """Test registration with weak password"""
        auth_service = AuthService(db)
        
        # Password too short
        user_data = UserRegister(
            email="test@example.com",
            password="Short1"  # Less than 8 chars
        )
        
        with pytest.raises(ValueError):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_password_no_uppercase(self, db):
        """Test registration with password lacking uppercase"""
        auth_service = AuthService(db)
        
        user_data = UserRegister(
            email="test@example.com",
            password="password123!"  # No uppercase
        )
        
        with pytest.raises(ValueError, match="заглавные"):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_password_hashed(self, db):
        """Test that password is properly hashed during registration"""
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        user_data = UserRegister(
            email="hashtest@example.com",
            password="MyPassword123!"
        )
        
        result = await auth_service.register(user_data)
        
        # Retrieve user from DB
        user = user_repo.get_by_email("hashtest@example.com")
        
        # Password should be hashed, not plain
        assert user.hashed_password != "MyPassword123!"
        assert user.hashed_password.startswith("$2b$")  # bcrypt format

    @pytest.mark.asyncio
    async def test_login_success(self, db):
        """Test successful login"""
        auth_service = AuthService(db)
        
        # Register user
        register_data = UserRegister(
            email="logintest@example.com",
            password="LoginPass123!"
        )
        await auth_service.register(register_data)
        
        # Login
        login_data = UserLogin(
            email="logintest@example.com",
            password="LoginPass123!"
        )
        
        result = await auth_service.login(login_data)
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert "user" in result
        assert result["user"]["email"] == "logintest@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, db):
        """Test login with incorrect password"""
        auth_service = AuthService(db)
        
        # Register user
        register_data = UserRegister(
            email="wrongpass@example.com",
            password="CorrectPass123!"
        )
        await auth_service.register(register_data)
        
        # Try login with wrong password
        login_data = UserLogin(
            email="wrongpass@example.com",
            password="WrongPass123!"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login(login_data)

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, db):
        """Test login with non-existent email"""
        auth_service = AuthService(db)
        
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="SomePass123!"
        )
        
        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login(login_data)

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, db):
        """Test login with inactive (blocked) user"""
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        # Register user
        register_data = UserRegister(
            email="blocked@example.com",
            password="BlockedPass123!"
        )
        await auth_service.register(register_data)
        
        # Deactivate user
        user = user_repo.get_by_email("blocked@example.com")
        user.is_active = False
        db.commit()
        
        # Try to login
        login_data = UserLogin(
            email="blocked@example.com",
            password="BlockedPass123!"
        )
        
        with pytest.raises(ValueError, match="blocked"):
            await auth_service.login(login_data)

    @pytest.mark.asyncio
    async def test_login_updates_last_login(self, db):
        """Test that login updates last_login timestamp"""
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        # Register user
        register_data = UserRegister(
            email="timestamp@example.com",
            password="TimestampPass123!"
        )
        await auth_service.register(register_data)
        
        # Check initial last_login
        user_before = user_repo.get_by_email("timestamp@example.com")
        assert user_before.last_login is None
        
        # Login
        login_data = UserLogin(
            email="timestamp@example.com",
            password="TimestampPass123!"
        )
        await auth_service.login(login_data)
        
        # Check updated last_login
        user_after = user_repo.get_by_email("timestamp@example.com")
        assert user_after.last_login is not None

    @pytest.mark.asyncio
    async def test_login_returns_valid_jwt_tokens(self, db):
        """Test that login returns decodable JWT tokens"""
        auth_service = AuthService(db)
        from app.utils.password_utils import JWTUtils
        
        # Register and login
        register_data = UserRegister(
            email="jwttest@example.com",
            password="JwtPass123!"
        )
        await auth_service.register(register_data)
        
        login_data = UserLogin(
            email="jwttest@example.com",
            password="JwtPass123!"
        )
        result = await auth_service.login(login_data)
        
        # Decode access token
        decoded_access = JWTUtils.decode_token(result["access_token"])
        assert decoded_access["email"] == "jwttest@example.com"
        assert "sub" in decoded_access
        assert "exp" in decoded_access
        
        # Decode refresh token
        decoded_refresh = JWTUtils.decode_token(result["refresh_token"])
        assert decoded_refresh["email"] == "jwttest@example.com"
        assert decoded_refresh.get("type") == "refresh"

    @pytest.mark.asyncio
    async def test_register_creates_default_username(self, db):
        """Test that username is auto-generated from email"""
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        user_data = UserRegister(
            email="autouser@example.com",
            password="AutoPass123!"
        )
        
        await auth_service.register(user_data)
        
        user = user_repo.get_by_email("autouser@example.com")
        assert user.username == "autouser"  # Part before @

    @pytest.mark.asyncio
    async def test_register_user_has_default_role(self, db):
        """Test that new users get default 'user' role"""
        auth_service = AuthService(db)
        user_repo = UserRepository(db)
        
        user_data = UserRegister(
            email="roletest@example.com",
            password="RolePass123!"
        )
        
        await auth_service.register(user_data)
        
        user = user_repo.get_by_email("roletest@example.com")
        assert user.role == "user"
        assert user.role != "admin"
