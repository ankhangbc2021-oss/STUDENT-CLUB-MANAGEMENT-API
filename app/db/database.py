"""
app/db/database.py
engine, SessionLocal, Base, get_db
"""

import ssl

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# Tạo context SSL mặc định (hỗ trợ kết nối an toàn tới Aiven)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = (
    ssl.CERT_NONE
)  # Bỏ qua xác thực chứng chỉ CA nội bộ nếu không đính kèm file CA

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True,
    pool_recycle=3600,
)
engine = create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base
Base = declarative_base()


def get_db():
    """
    Dependency generator để cung cấp database session cho mỗi request.
    Đảm bảo session được đóng sau khi request hoàn thành (Exception handling scope).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
