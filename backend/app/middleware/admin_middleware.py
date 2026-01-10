from fastapi import HTTPException, Depends
from app.middleware.auth import get_current_user

async def require_admin(current_user: dict = Depends(get_current_user)):

    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required. You don't have permission to access this resource."
        )
    return current_user
