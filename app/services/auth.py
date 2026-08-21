"""
app/services/auth.py

Trang dùng để đăng ký và đăng nhập
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.models.user import User
from app.schemas.user import RefreshTokenRequest, UserCreate, UserLogin


def create_user(db: Session, user_data: UserCreate):
    """
    Đăng ký tài khoản:
    1. Kiểm tra email có tồn tại chưa
    2. Nếu tồn tại ném lỗi 400
    3. Băm mật khẩu
    4. Lưu thông tin
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email đã tồn tại"
        )

    hashed_password = security.hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": "Tạo tài khoản thành công",
        "data": new_user,
    }


def login_user(db: Session, user_data: UserLogin):
    """
    Đăng nhập:
    1. Tìm người dùng trong database
    2. Nếu không thấy trả về 400
    3. Trả về thông tin nếu thành công
    """

    user = db.query(User).filter(User.email == user_data.email).first()

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động hoặc bị khóa",
        )

    if not user or not security.verify_password(user_data.password, user.password_hash):
        # Ghi lại số lần đăng nhập thất bại
        remaining = security.record_failed_login(user_data.email)

        if remaining == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Bạn đã nhập sai 3 lần liên tiệp tài khoản bị tạm khóa 5 phút",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Email hoặc mật khẩu không chính xác! Bạn còn {remaining} lần thử."
            ),
        )

    return user


def refresh_token(db: Session, payload: RefreshTokenRequest):
    """Làm mới token"""

    # 1. Giải mã & kiểm tra Refresh Token
    user_id = security.verify_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Kiểm tra tài khoản trong DB
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa",
        )

    return user
