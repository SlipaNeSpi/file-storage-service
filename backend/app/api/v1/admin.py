from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.services.admin_service import AdminService
from app.middleware.admin_middleware import require_admin
from app.database import get_db
from typing import Optional

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ==================

@router.get("/users", summary="Get all users (Admin)")
async def get_all_users(
    skip: int = Query(0),
    limit: int = Query(100, le=500),
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with statistics.
    Admin only.
    """
    service = AdminService(db)
    users = service.get_all_users(skip, limit)
    return {
        "total": len(users),
        "users": users
    }

@router.get("/users/{user_id}", summary="Get user details (Admin)")
async def get_user_details(
    user_id: str,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about specific user.
    Includes files, statistics, and activity.
    """
    try:
        service = AdminService(db)
        user_info = service.get_user_details(user_id)
        return user_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/users/{user_id}/toggle-status", summary="Block/Unblock user (Admin)")
async def toggle_user_status(
    user_id: str,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Block or unblock user account.
    Toggles is_active flag.
    """
    try:
        service = AdminService(db)
        result = service.toggle_user_status(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/users/{user_id}/role", summary="Change user role (Admin)")
async def change_user_role(
    user_id: str,
    new_role: str = Query(..., regex="^(user|admin)$"),
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Change user role between 'user' and 'admin'.
    """
    try:
        service = AdminService(db)
        result = service.change_user_role(user_id, new_role)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}", summary="Delete user (Admin)")
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Permanently delete user and all their files.
    This action cannot be undone!
    """
    try:
        service = AdminService(db)
        result = service.delete_user(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ================== УПРАВЛЕНИЕ ФАЙЛАМИ ==================

@router.get("/files", summary="Get all files (Admin)")
async def get_all_files(
    skip: int = Query(0),
    limit: int = Query(100, le=500),
    file_type: Optional[str] = Query(None),
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all files in the system.
    Can filter by file type.
    """
    service = AdminService(db)
    files = service.get_all_files(skip, limit, file_type)
    return {
        "total": len(files),
        "filters": {"file_type": file_type},
        "files": files
    }

@router.delete("/files/{file_id}", summary="Delete file (Admin)")
async def delete_file(
    file_id: str,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete any file in the system (admin override).
    File owner will lose access to the file.
    """
    try:
        service = AdminService(db)
        result = service.delete_file_by_admin(file_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ================== СТАТИСТИКА И DASHBOARD ==================

@router.get("/dashboard", summary="Get dashboard statistics (Admin)")
async def get_dashboard(
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics:
    - User counts
    - File counts
    - Storage usage
    - File type distribution
    """
    service = AdminService(db)
    stats = service.get_dashboard_stats()
    return stats

@router.get("/top-users", summary="Get top users by storage (Admin)")
async def get_top_users(
    limit: int = Query(10, le=50),
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get top users ranked by storage usage.
    Useful for identifying heavy users.
    """
    service = AdminService(db)
    top_users = service.get_top_users_by_storage(limit)
    return {
        "limit": limit,
        "top_users": top_users
    }
