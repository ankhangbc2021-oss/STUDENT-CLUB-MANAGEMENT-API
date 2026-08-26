"""
app/main.py
Khởi tạo FastAPI app, include routers, middleware
"""

# import fastapi
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# import slowapi dùng để rate limit
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import app.models  # Tạo đủ bảng vì có __init__.py nên gộm tất cả bảng

# import core
from app.core.config import settings
from app.core.limiter import limiter

# import db
from app.db.database import Base, engine

# import router
from app.routers import activity, auth, club, users

# Khời tạo ứng dụng FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPION,
    version=settings.APP_VERSION,
)

origins_whitelist = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_whitelist,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Gắn limiter vào app state và đăng ký handler xửa lý lỗi 429
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
    """Lỗi 422"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
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

# Nhúng router xử lý club (chia cho dễ xử lý)
app.include_router(club.router)
app.include_router(club.router_log)
app.include_router(club.router_member)
app.include_router(club.router_activity)

# Nhúng router xử lý users
app.include_router(users.router)


# HEALTH-CHECK ENDPOINT
@app.get("/health", tags=["Root"], summary="Kiểm tra sever có hoạt động không")
def health_check():
    """Kiểm tra sever còn hoạt động không"""
    return {"status": "healthy", "message": "Sever FastAPI đang hoạt động bình thường"}


@app.get("/", tags=["Root"], summary="Chào mừng")
def root():
    """Mặc định"""
    return {
        "message": "Chào mừng bạn đến với ứng dụng Student Club Management API. Hãy truy cập /docs"
    }
