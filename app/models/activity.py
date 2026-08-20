"""
app/models/activity.py
Model ClubActivity
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ClubActivity(Base):
    """Cấu hình bảng ClubActivity (Hoạt động CLB)"""

    __tablename__ = "club_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(
        String(50), default="TODO", nullable=False
    )  # TODO / IN_PROGRESS / DONE
    priority = Column(
        String(50), default="MEDIUM", nullable=False
    )  # LOW / MEDIUM / HIGH
    due_date = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc)
    )

    # Liên kết
    club = relationship("Club", back_populates="activities")
    assignee = relationship("User", back_populates="assigned_activities")
