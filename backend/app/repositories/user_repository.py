from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.schemas.user import User
from uuid import UUID
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == UUID(user_id)).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по имени"""
        return self.db.query(User).filter(User.username == username).first()

    def create(self, email: str, username: str, hashed_password: str) -> User:
        """Создать нового пользователя"""
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all(self, skip: int = 0, limit: int = 100):
        """Получить всех пользователей"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update_last_login(self, user_id: str):
        """Обновить время последнего входа"""
        from datetime import datetime
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
