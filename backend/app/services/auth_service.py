from sqlalchemy.orm import Session
from app.models.auth import UserRegister, UserLogin
from app.utils.password_utils import PasswordUtils, JWTUtils
from app.utils.validators import EmailValidator
from app.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserRegister) -> dict:
        if not EmailValidator.validate(user_data.email):
            raise ValueError("Invalid email format")

        if self.user_repo.get_by_email(user_data.email):
            raise ValueError("User with this email already exists")

        is_valid, message = PasswordUtils.validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(message)

        hashed_password = PasswordUtils.hash_password(user_data.password)
        username = user_data.email.split("@")[0]

        new_user = self.user_repo.create(
            email=user_data.email,
            username=username,
            hashed_password=hashed_password,
        )

        return {
            "id": str(new_user.id),
            "email": new_user.email,
            "message": "User registered successfully. Please login.",
        }

    async def login(self, login_data: UserLogin) -> dict:
        user = self.user_repo.get_by_email(login_data.email)

        if not user or not PasswordUtils.verify_password(
            login_data.password, user.hashed_password
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is blocked")

        access_token = JWTUtils.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )

        refresh_token = JWTUtils.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        self.user_repo.update_last_login(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
            },
        }
