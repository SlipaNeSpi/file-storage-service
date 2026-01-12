"""
Unit tests for password utilities
Tests password hashing, verification and strength validation
"""
import pytest
from app.utils.password_utils import PasswordUtils, JWTUtils
from datetime import timedelta


class TestPasswordUtils:
    """Test suite for PasswordUtils class"""

    def test_hash_password_creates_valid_hash(self):
        """Test that password is properly hashed"""
        password = "TestPassword123!"
        hashed = PasswordUtils.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # bcrypt hashes are long
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_verify_password_correct(self):
        """Test verification with correct password"""
        password = "MySecurePass123!"
        hashed = PasswordUtils.hash_password(password)
        
        result = PasswordUtils.verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test verification with incorrect password"""
        password = "MySecurePass123!"
        wrong_password = "WrongPassword456!"
        hashed = PasswordUtils.hash_password(password)
        
        result = PasswordUtils.verify_password(wrong_password, hashed)
        assert result is False

    def test_different_passwords_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "TestPassword123!"
        hash1 = PasswordUtils.hash_password(password)
        hash2 = PasswordUtils.hash_password(password)
        
        assert hash1 != hash2  # Salting ensures different hashes
        assert PasswordUtils.verify_password(password, hash1)
        assert PasswordUtils.verify_password(password, hash2)

    # Password strength validation tests
    def test_password_too_short(self):
        """Test validation fails for passwords < 8 characters"""
        is_valid, message = PasswordUtils.validate_password_strength("Short1!")
        
        assert is_valid is False
        assert "минимум 8 символов" in message

    def test_password_no_uppercase(self):
        """Test validation fails without uppercase letters"""
        is_valid, message = PasswordUtils.validate_password_strength("password123!")
        
        assert is_valid is False
        assert "заглавные буквы" in message

    def test_password_no_lowercase(self):
        """Test validation fails without lowercase letters"""
        is_valid, message = PasswordUtils.validate_password_strength("PASSWORD123!")
        
        assert is_valid is False
        assert "строчные буквы" in message

    def test_password_no_digits(self):
        """Test validation fails without digits"""
        is_valid, message = PasswordUtils.validate_password_strength("PasswordTest!")
        
        assert is_valid is False
        assert "цифры" in message

    def test_password_valid_strong(self):
        """Test validation passes for strong password"""
        is_valid, message = PasswordUtils.validate_password_strength("SecurePass123!")
        
        assert is_valid is True
        assert message == "OK"

    @pytest.mark.parametrize("password", [
        "Aa1aaaaa",  # Minimum requirements
        "MyPassword123",
        "SuperSecure2024!",
        "C0mpl3xP@ssw0rd",
    ])
    def test_various_valid_passwords(self, password):
        """Test multiple valid password formats"""
        is_valid, message = PasswordUtils.validate_password_strength(password)
        assert is_valid is True


class TestJWTUtils:
    """Test suite for JWT token utilities"""

    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = JWTUtils.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long strings

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = JWTUtils.create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": "user123", "email": "test@example.com", "role": "user"}
        token = JWTUtils.create_access_token(data)
        
        decoded = JWTUtils.decode_token(token)
        
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "user"
        assert "exp" in decoded  # Expiration time

    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises error"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(ValueError, match="Invalid token"):
            JWTUtils.decode_token(invalid_token)

    def test_token_with_custom_expiration(self):
        """Test token with custom expiration time"""
        data = {"sub": "user123"}
        custom_delta = timedelta(minutes=60)
        token = JWTUtils.create_access_token(data, expires_delta=custom_delta)
        
        decoded = JWTUtils.decode_token(token)
        assert "exp" in decoded

    def test_access_and_refresh_tokens_different(self):
        """Test that access and refresh tokens are different"""
        data = {"sub": "user123", "email": "test@example.com"}
        access_token = JWTUtils.create_access_token(data)
        refresh_token = JWTUtils.create_refresh_token(data)
        
        assert access_token != refresh_token
        
        # Refresh token should have 'type' field
        decoded_refresh = JWTUtils.decode_token(refresh_token)
        assert decoded_refresh.get("type") == "refresh"
