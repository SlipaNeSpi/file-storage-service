from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.gateway import router
from app.database import init_db

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up File Storage Service...")
    init_db()
    yield
    print("🛑 Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Secure file upload and storage service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/", tags=["root"])
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/docs", "redoc": "/redoc"}
