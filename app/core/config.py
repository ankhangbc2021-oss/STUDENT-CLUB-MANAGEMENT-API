"""
app/core/cofig.py
Đọc biến môi trường và settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Setting"""

    # Cấu hình ứng dụng
    APP_NAME: str = "STUDENT CLUB MANAGEMENT API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPION: str = "Quản lý câu lạc bộ sinh viên"

    # Cấu hình Database
    DATABASE_URL: str

    # Cấu hình JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Cấu hình đăng nhập (rate limit)
    MAX_ATTEMPTS: int
    LOCK_MINUTES: int

    # Cấu hình CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        """Chỉ định đọc file .env"""

        env_file = ".env"
        env_file_config = "utf-8"


# Khởi chạy settings
settings = Settings()
