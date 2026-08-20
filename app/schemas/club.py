"""
app/schemas/club.py
Tạo Base/Create/Update/Response schema

Có 2 Schemas Gồm Club / ClubMember
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ClubRole(str, Enum):
    """Định nghĩa Enum cho Role"""

    OWNER = "OWNER"
    MEMBER = "MEMBER"


# --- Schemas ClubBase ---
class ClubBase(BaseModel):
    """Lớp cơ bản Club"""

    name: str = Field(..., min_length=1)
    description: str | None = None
    owner_id: int = Field(...)


class CreateClub(ClubBase):
    """Lớp tạo Club(Câu lạc bộ)"""


class UpdateClub(ClubBase):
    """Lớp cập nhật Club(Câu lạc bộ)"""


class DeleteClub(ClubBase):
    """Lớp xóa Club(Câu lạc bộ)"""


class ClubResponse(ClubBase):
    """Lớp trả về Club(Câu lạc bộ)"""

    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Schemas ClubMember ---
class ClubMemberBase(BaseModel):
    """Lớp cơ bản ClubMember"""

    user_id: int = Field(...)
    role: ClubRole = ClubRole.MEMBER


class CreateClubMember(ClubMemberBase):
    """Lớp tạo ClubMember(Thành viên câu lạc bộ)"""


class DeleteClubMember(ClubMemberBase):
    """Xóa ClubMember(Thành viên câu lạc bộ)"""


class ClubMemberResponse(ClubMemberBase):
    """Lớp trả về ClubMember(Thành viên câu lạc bộ)"""

    id: int
    club_id: int
    joined_at: datetime | None = None
