"""
app/core/security.py
Hash password, JWT encode/decode
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# Bộ nhớ tạm lưu số lần gõ sai {"email": {"count": 2, "locked_until": datetime}}
FAILED_LOGINS: dict[str, dict] = {}
MAX_ATTEMPTS = settings.MAX_ATTEMPTS
LOCK_MINUTES = settings.LOCK_MINUTES


# <--- Check rate limit --->
def check_login_rate_limit(email: str) -> None:
    """Kiểm tra xem tài khoản có đang bị khóa không

    Args:
        email (str): nhận vào email
    """

    record = FAILED_LOGINS.get(email)
    if not record:
        return

    locked_until: datetime | None = record.get(
        "locked_until"
    )  # Lấy dữ liệu Any do chưa biết
    now = datetime.now(timezone.utc)  # Lấy thời gian hiện tại

    if locked_until and locked_until > now:
        time_diff: timedelta = (
            locked_until - now
        )  # Phút còn lại vd(khóa tới 10:05 hiện tại 10:00 còn 5p)
        remain = int(time_diff.total_seconds())  # Đổi sang giây
        raise ValueError(f"Tài khoản bị tạm khóa. Vui lòng thử lại sau {remain}s.")

    # Đã qua thời gian khóa -> Dọn dẹp bộ nhớ
    if locked_until and locked_until <= now:
        FAILED_LOGINS.pop(email, None)


def record_failed_login(email: str) -> int:
    """Ghi nhận 1 lần nhập sai, trả về số lần thử còn lại"""
    now = datetime.now(timezone.utc)

    if email not in FAILED_LOGINS:
        FAILED_LOGINS[email] = {"count": 1, "locked_until": None}
    else:
        FAILED_LOGINS[email]["count"] += 1

    count = FAILED_LOGINS[email]["count"]

    # Kiểm tra số lần nhập còn lại nếu lên vượt giới hạn thì lập tức tạo thời gian khóa
    if count >= MAX_ATTEMPTS:
        FAILED_LOGINS[email]["locked_until"] = now + timedelta(minutes=LOCK_MINUTES)
        return 0

    return MAX_ATTEMPTS - count


def reset_failed_login(email: str) -> None:
    """Xóa lịch sử sai sau khi đăng nhập thành công"""
    FAILED_LOGINS.pop(email, None)


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
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
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
