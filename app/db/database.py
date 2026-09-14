"""
app/db/database.py
engine, SessionLocal, Base, get_db
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

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
