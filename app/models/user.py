"""
app/models/user.py
Model User
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """Cấu hình bảng"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    # Nhận role USER / ADMIN
    role = Column(String(50), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    clubs = relationship("Club", back_populates="users")
    club_members = relationship("ClubMember", back_populates="users")
    club_activities = relationship("ClubActivity", back_populates="users")
