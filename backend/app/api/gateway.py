from fastapi import APIRouter
from app.api.v1 import auth, files, admin

router = APIRouter()

router.include_router(auth.router)
router.include_router(files.router)
router.include_router(admin.router)