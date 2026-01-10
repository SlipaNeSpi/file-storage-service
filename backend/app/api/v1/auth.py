from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.auth import UserRegister, UserLogin, TokenResponse
from app.services.auth_service import AuthService
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=dict,
    summary="Register new user",
)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        result = await service.register(user_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        result = await service.login(login_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed")
