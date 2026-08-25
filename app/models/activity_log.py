"""
app/models/activity_log.py
Viết lịch sử thao tác
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class ActivityAction(str, Enum):
    """
    Khởi tạo khái nệm enum
    - CREATE_CLUB
    - UPDATE_CLUB
    - DELETE_CLUB
    - ADD_MEMBER
    - REMOVE_MEMBER
    - UPDATE_MEMBER_ROLE

    ---
    Thêm 2 action kiểm tra để limit
    - LOGIN_FAILED
    - ACCOUNT_LOCKED
    """

    # CLB
    CREATE_CLUB = "CREATE_CLUB"
    UPDATE_CLUB = "UPDATE_CLUB"
    DELETE_CLUB = "DELETE_CLUB"

    # Thành viên
    ADD_MEMBER = "ADD_MEMBER"
    REMOVE_MEMBER = "REMOVE_MEMBER"
    UPDATE_MEMBER_ROLE = "UPDATE_MEMBER_ROLE"

    # 2 Action để rate limit
    LOGIN_FAILED = "LOGIN_FAILED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"


class ActivityLog(Base):
    """Lớp tạo bảng log"""

    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    club_id = Column(Integer, index=True)
    action = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
