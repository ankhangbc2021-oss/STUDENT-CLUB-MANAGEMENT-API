"""
app/main.py
Khởi tạo FastAPI app, include routers, middleware
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models
from app.core.config import settings
from app.db.database import Base, engine
from app.routers import activity, auth, club, users

# Khời tạo ứng dụng FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPION,
    version=settings.APP_VERSION,
)

origins_whitelist = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_whitelist,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.exception_handler(HTTPException)
async def custom_error_handler(_request: Request, exc: HTTPException):
    """Khi có lỗi, ép trả về đúng JSON"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
):
    """Lỗi 400"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Dữ liệu request không hợp lệ",
            "errors": exc.errors(),
        },
    )


# Tạo bảng trong Database
Base.metadata.create_all(bind=engine)

# Nhúng router xử lý auth
app.include_router(auth.router)

# Nhúng router xử lý activity
app.include_router(activity.router)

# Nhúng router xử lý club
app.include_router(club.router)

# Nhúng router xử lý users
app.include_router(users.router)


# HEALTH-CHECK ENDPOINT
@app.get("/health", tags=["Root"])
def health_check():
    """Kiểm tra sever còn hoạt động không"""
    return {"status": "healthy", "message": "Sever FastAPI đang hoạt động bình thường"}


@app.get("/", tags=["Root"])
def root():
    """Mặc định"""
    return {
        "message": "Chào mừng bạn đến với ứng dụng Student Club Management API. Hãy truy cập /docs"
    }
