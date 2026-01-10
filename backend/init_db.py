"""
Скрипт для инициализации базы данных и создания тестовых пользователей
"""
from app.database import engine, SessionLocal
from app.schemas.base import Base
from app.schemas.user import User
from app.schemas.file import File
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import PasswordUtils


def init_database():
    """Пересоздать все таблицы"""
    print("🗑️  Удаление существующих таблиц...")
    Base.metadata.drop_all(bind=engine)

    print("📊 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы: users, files")


def create_admin():
    """Создать администратора"""
    db = SessionLocal()
    user_repo = UserRepository(db)

    try:
        # Проверяем, существует ли админ
        existing_admin = user_repo.get_by_email("admin@example.com")
        if existing_admin:
            print("⚠️  Admin уже существует")
            return

        # Создаём админа
        hashed_password = PasswordUtils.hash_password("Admin123")
        admin_user = user_repo.create(
            email="admin@example.com",
            username="admin",
            hashed_password=hashed_password
        )

        admin_user.role = "admin"
        db.commit()

        print(f"✅ Admin создан: {admin_user.email} (role: {admin_user.role})")
    except Exception as e:
        print(f"❌ Ошибка при создании админа: {e}")
        db.rollback()
    finally:
        db.close()


def create_test_user():
    """Создать тестового пользователя"""
    db = SessionLocal()
    user_repo = UserRepository(db)

    try:
        # Проверяем, существует ли пользователь
        existing_user = user_repo.get_by_email("user@example.com")
        if existing_user:
            print("⚠️  Test user уже существует")
            return

        # Создаём пользователя
        hashed_password = PasswordUtils.hash_password("User123!")
        user = user_repo.create(
            email="user@example.com",
            username="testuser",
            hashed_password=hashed_password
        )

        print(f"✅ User создан: {user.email} (role: {user.role})")
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Инициализация базы данных")
    print("=" * 50)

    init_database()
    create_admin()
    create_test_user()

    print("\n" + "=" * 50)
    print("✅ Инициализация завершена!")
    print("=" * 50)
    print("\n📝 Данные для входа:")
    print("   Admin: admin@example.com / Admin123")
    print("   User:  user@example.com / User123!")
