"""
app/models/club.py
Model Club / ClubMember
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Club(Base):
    """Cấu hình bảng Club (Câu lạc bộ)"""

    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime, default=None, onupdate=lambda: datetime.now(timezone.utc)
    )

    # Liên kết
    owner = relationship("User", back_populates="owned_clubs")
    members = relationship(
        "ClubMember", back_populates="club", cascade="all, delete-orphan"
    )
    activities = relationship(
        "ClubActivity", back_populates="club", cascade="all, delete-orphan"
    )


class ClubMember(Base):
    """Cấu hình bảng ClubMember (Thành viên CLB)"""

    __tablename__ = "club_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False, default="MEMBER")  # OWNER / MEMBER
    joined_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Đảm bảo 1 user không bị thêm trùng 2 lần vào cùng 1 CLB
    __table_args__ = (UniqueConstraint("club_id", "user_id", name="uq_club_member"),)

    # Liên kết
    club = relationship("Club", back_populates="members")
    user = relationship("User", back_populates="club_memberships")
