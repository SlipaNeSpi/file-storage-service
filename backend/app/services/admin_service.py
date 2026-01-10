from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.repositories.user_repository import UserRepository
from app.repositories.file_repository import FileRepository
from app.schemas.user import User
from app.schemas.file import File
from typing import List, Dict, Any
from uuid import UUID


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.file_repo = FileRepository(db)

    # ================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ==================

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Получить всех пользователей с дополнительной информацией"""
        users = self.user_repo.get_all(skip, limit)

        result = []
        for user in users:
            # Подсчитываем статистику по файлам пользователя
            user_files = self.db.query(File).filter(
                File.owner_id == user.id,
                File.is_deleted == False
            ).all()

            total_size = sum(f.file_size for f in user_files)
            file_count = len(user_files)

            result.append({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "stats": {
                    "file_count": file_count,
                    "total_size": total_size,
                    "total_size_mb": round(total_size / 1024 / 1024, 2)
                }
            })

        return result

    def get_user_details(self, user_id: str) -> Dict:
        """Детальная информация о пользователе"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Получаем файлы пользователя
        files = self.db.query(File).filter(
            File.owner_id == UUID(user_id),
            File.is_deleted == False
        ).all()

        total_size = sum(f.file_size for f in files)

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "stats": {
                "file_count": len(files),
                "total_size": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            },
            "files": [
                {
                    "id": str(f.id),
                    "filename": f.original_name,
                    "size": f.file_size,
                    "type": f.file_type,
                    "created_at": f.created_at.isoformat()
                }
                for f in files[:10]  # Показываем последние 10 файлов
            ]
        }

    def toggle_user_status(self, user_id: str) -> Dict:
        """Блокировка/Разблокировка пользователя"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.is_active = not user.is_active
        self.db.commit()

        return {
            "user_id": str(user.id),
            "is_active": user.is_active,
            "message": f"User {'activated' if user.is_active else 'blocked'}"
        }

    def change_user_role(self, user_id: str, new_role: str) -> Dict:
        """Изменить роль пользователя"""
        if new_role not in ['user', 'admin']:
            raise ValueError("Invalid role. Must be 'user' or 'admin'")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.role = new_role
        self.db.commit()

        return {
            "user_id": str(user.id),
            "role": user.role,
            "message": f"User role changed to {new_role}"
        }

    def delete_user(self, user_id: str) -> Dict:
        """Удалить пользователя (полное удаление)"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Мягкое удаление всех файлов пользователя
        files = self.db.query(File).filter(File.owner_id == UUID(user_id)).all()
        for file in files:
            file.is_deleted = True

        # Удаление пользователя
        self.db.delete(user)
        self.db.commit()

        return {
            "user_id": user_id,
            "message": f"User deleted along with {len(files)} files"
        }

    # ================== УПРАВЛЕНИЕ ФАЙЛАМИ ==================

    def get_all_files(
            self,
            skip: int = 0,
            limit: int = 100,
            file_type: str = None
    ) -> List[Dict]:
        """Получить все файлы в системе"""
        query = self.db.query(File).filter(File.is_deleted == False)

        if file_type:
            query = query.filter(File.file_type.contains(file_type))

        files = query.order_by(desc(File.created_at)).offset(skip).limit(limit).all()

        return [
            {
                "id": str(f.id),
                "filename": f.original_name,
                "size": f.file_size,
                "size_mb": round(f.file_size / 1024 / 1024, 2),
                "type": f.file_type,
                "owner": {
                    "id": str(f.owner_id),
                    "email": f.owner.email,
                    "username": f.owner.username
                },
                "created_at": f.created_at.isoformat()
            }
            for f in files
        ]

    def delete_file_by_admin(self, file_id: str) -> Dict:
        """Удаление файла администратором"""
        file = self.db.query(File).filter(
            File.id == UUID(file_id),
            File.is_deleted == False
        ).first()

        if not file:
            raise ValueError("File not found")

        # Мягкое удаление
        file.is_deleted = True
        self.db.commit()

        return {
            "file_id": file_id,
            "filename": file.original_name,
            "owner": str(file.owner_id),
            "message": "File deleted by admin"
        }

    # ================== СТАТИСТИКА ==================

    def get_dashboard_stats(self) -> Dict:
        """Получить общую статистику для dashboard"""
        # Подсчёт пользователей
        total_users = self.db.query(func.count(User.id)).scalar()
        active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        admin_users = self.db.query(func.count(User.id)).filter(User.role == 'admin').scalar()

        # Подсчёт файлов
        total_files = self.db.query(func.count(File.id)).filter(File.is_deleted == False).scalar()
        deleted_files = self.db.query(func.count(File.id)).filter(File.is_deleted == True).scalar()

        # Объём хранилища
        total_storage = self.db.query(func.sum(File.file_size)).filter(File.is_deleted == False).scalar() or 0
        total_storage_gb = round(total_storage / 1024 / 1024 / 1024, 2)

        # Распределение по типам файлов
        file_types = self.db.query(
            File.file_type,
            func.count(File.id).label('count')
        ).filter(File.is_deleted == False).group_by(File.file_type).all()

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "blocked": total_users - active_users,
                "admins": admin_users
            },
            "files": {
                "total": total_files,
                "deleted": deleted_files,
                "active": total_files
            },
            "storage": {
                "total_bytes": total_storage,
                "total_gb": total_storage_gb,
                "average_file_size_mb": round((total_storage / total_files / 1024 / 1024) if total_files > 0 else 0, 2)
            },
            "file_types": [
                {"type": ft.file_type, "count": ft.count}
                for ft in file_types
            ]
        }

    def get_top_users_by_storage(self, limit: int = 10) -> List[Dict]:
        """Топ пользователей по объёму хранилища"""
        results = self.db.query(
            User.id,
            User.email,
            User.username,
            func.count(File.id).label('file_count'),
            func.sum(File.file_size).label('total_size')
        ).join(File, User.id == File.owner_id).filter(
            File.is_deleted == False
        ).group_by(User.id).order_by(desc('total_size')).limit(limit).all()

        return [
            {
                "user_id": str(r.id),
                "email": r.email,
                "username": r.username,
                "file_count": r.file_count,
                "total_size": r.total_size,
                "total_size_mb": round(r.total_size / 1024 / 1024, 2)
            }
            for r in results
        ]
