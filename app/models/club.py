"""
app/models/club.py
Model Club / ClubMember
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Boolean, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Club(Base):
    """Cấu hình bảng Club"""

    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    users = relationship("User", back_populates="clubs")
    club_members = relationship("ClubMember", back_populates="clubs")


class ClubMember(Base):
    """Cấu hình ClubMember"""

    __tablename__ = "club_members"

    club_id = Column(Integer, ForeignKey("clubs.id"), primary_key=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, unique=True)
    # Nhận role OWNER / MEMBER
    role = Column(String(50), nullable=False)
    joined_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    clubs = relationship("Club", back_populates="club_members")
    users = relationship("User", back_populates="club_members")
