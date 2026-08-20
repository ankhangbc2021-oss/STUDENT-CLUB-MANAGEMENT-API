"""
app/models/user.py
Model User
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class SystemRole(str, Enum):
    """Định nghĩa Enum (USER / ADMIN)"""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """Cấu hình bảng User"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=SystemRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc))

    # Liên kết
    owned_clubs = relationship("Club", back_populates="owner")
    club_memberships = relationship("ClubMember", back_populates="user")
    assigned_activities = relationship("ClubActivity", back_populates="assignee")