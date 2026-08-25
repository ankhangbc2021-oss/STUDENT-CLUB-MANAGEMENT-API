"""
app/routers/auth.py
Register/Login
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.limiter import limiter
from app.db.database import get_db
from app.schemas.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services import auth

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Khai báo Type dùng chung


@router.post(
    path="/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint Đăng ký tài khoản:
    - Nhận thông tin email, password, role, fullname
    - Gọi service để xử lý
    - Trả về thông tin UserResponse
    """
    new_user = auth.create_user(db=db, user_data=data)

    return new_user


@router.post(
    path="/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập và nhận JWT",
)
@limiter.limit("5/minute")  # Giới hạn 5 lần / phút mối IP
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint Đăng nhập:
    - Kiểm tra giới hạn rate limit & khóa tài khoản
    - Nhận vào email, password
    - Gọi và xác nhận
    - Reset bộ nhớ đệm
    - Tạo và trả JWT
    """
    # Kiểm tra có khóa không vì nhập sai quá 3 lần
    try:
        security.check_login_rate_limit(data.email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)
        ) from e

    user = auth.login_user(db=db, user_data=data)

    # Xóa lịch sử thử sai
    security.reset_failed_login(data.email)

    access_token = security.create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )
    new_refresh_token = security.create_refresh_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )

    return TokenResponse(
        status_code=200,
        message="Đăng nhập thành công",
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        data=user,
    )


@router.post(
    path="/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Cấp lại access token",
)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Cấp lại Access Token mới từ Refresh Token:
    1. Kiểm tra tính hợp lệ và thời hạn của refresh token
    2. Xác minh user trong database
    3. Tạo access token mới
    """
    user = auth.refresh_token(db, payload)

    # 3. Tạo access token mới
    new_access_token = security.create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role}
    )

    return TokenResponse(
        status_code=200,
        message="Cấp lại token thành công",
        access_token=new_access_token,
        refresh_token=payload.refresh_token,  # Giữ nguyên refresh token cũ hoặc sinh mới
        token_type="bearer",
        data=user,
    )
