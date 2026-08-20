"""
app/db/database.py
engine, SessionLocal, Base, get_db
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
