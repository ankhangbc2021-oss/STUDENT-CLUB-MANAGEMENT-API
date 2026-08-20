"""
app/models/activity.py
Model ClubActivity
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ClubActivity(Base):
    """Cấu hình bảng ClubActivity"""

    __tablename__ = "club_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # Người được giao
    status = Column(String(50), nullable=False)  # Nhận TODO / IN_PROGRESS / DONE
    priority = Column(String(50), nullable=False)  # LOW / MEDIUM / HIGH
    due_date = Column(DateTime)  # Hạn xử lý
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    clubs = relationship("Club", back_populates="club_activities")
    users = relationship("User", back_populates="club_activities")
