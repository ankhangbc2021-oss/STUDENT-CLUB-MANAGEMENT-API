"""
app/core/security.py
Hash password, JWT encode/decode
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str, cost_fastor: int = 12) -> str:
    """
    Hash mật khẩu bằng thuật toán bcrypt.

    Args:
        password (str): Mật khẩu dạng plaintext cần được hash.
        cost_factor (int, optional): Độ mạnh của quá trình hash. Giá trị càng lớn
            thì việc hash càng tốn thời gian. Mặc định là 12.

    Returns:
        str: Mật khẩu đã được hash.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=cost_fastor)
    hashed_bytes = bcrypt.hashpw(password=password_bytes, salt=salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu người dùng có khớp với mật khẩu đã được hash hay không.

    Args:
        plain_password (str): Mật khẩu dạng plaintext do người dùng nhập.
        hashed_password (str): Mật khẩu đã được hash và lưu trong database.

    Returns:
        bool: True nếu mật khẩu khớp, False nếu không khớp.
    """

    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict) -> str:
    """
    Tạo JWT access token từ dữ liệu được cung cấp.

    Args:
        data (dict): Dữ liệu được mã hóa và lưu vào JWT payload.

    Returns:
        str: JWT access token.
    """
    to_encode = data.copy()

    # Tính thời gian hết token - đọc từ config
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # Ký và tạo chỗi
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt
