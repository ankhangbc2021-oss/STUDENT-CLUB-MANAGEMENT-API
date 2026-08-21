"""
app/core/security.py
Hash password, JWT encode/decode
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# <--- Chỗ hash, very password và token --->
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
    to_encode.update({"exp": expire, "type": "access"})

    # Ký và tạo chỗi
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Tạo JWT refresh token từ dữ liệu được cung cấp.

    Args:
        data (dict): Dữ liệu được lưu trong JWT payload.

    Returns:
        str: JWT refresh token.
    """
    to_encode = data.copy()

    # Tính thời gian hết token - đọc từ config
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    # Ký và tạo chỗi
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_refresh_token(token: str) -> str | None:
    """
    Xác thực JWT refresh token và trả về user_id (sub) nếu hợp lệ.

    Args:
        token (str): JWT refresh token được gửi lên từ client.

    Returns:
        str | None: user_id nếu token hợp lệ và đúng type refresh, ngược lại trả về None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_type: str | None = payload.get("type")
        user_id: str | None = payload.get("id")

        # Bắt buộc phải là loại refresh token và có chứa user_id
        if token_type != "refresh":
            return None

        if not user_id:
            return None

        return str(user_id)
    except jwt.PyJWTError:
        # Bắt tất cả các lỗi của PyJWT (hết hạn, sai chữ ký, format sai...)
        return None
