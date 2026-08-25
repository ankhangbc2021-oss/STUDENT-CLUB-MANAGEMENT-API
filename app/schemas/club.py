"""
app/schemas/club.py
Tạo Base/Create/Update/Response schema

Có 2 Schemas Gồm Club / ClubMember
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClubRole(str, Enum):
    """Định nghĩa Enum cho Role"""

    OWNER = "OWNER"
    MEMBER = "MEMBER"


# --- Schemas ClubBase ---
class ClubBase(BaseModel):
    """Lớp cơ bản Club"""

    name: str = Field(..., min_length=1)
    description: str | None = None


class CreateClub(ClubBase):
    """Lớp tạo Club(Câu lạc bộ)"""


class UpdateClub(ClubBase):
    """Lớp cập nhật Club(Câu lạc bộ)"""


class ClubResponseBase(ClubBase):
    """Lớp trả về Club(Câu lạc bộ)"""

    id: int
    owner_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ClubResponse(BaseModel):
    """Lớp trả về Club(có mess và status_code)"""

    status_code: int
    message: str | None = None
    data: ClubResponseBase | None = []

    model_config = ConfigDict(from_attributes=True)


class ClubResponseList(BaseModel):
    """Lớp trả về danh sách câu lạc bộ"""

    status_code: int
    message: str | None = None
    data: list[ClubResponseBase] = []

    model_config = ConfigDict(from_attributes=True)


# --------------------------
# --- Schemas ClubMember ---
# --------------------------


class ClubMemberBase(BaseModel):
    """Lớp cơ bản ClubMember"""

    user_id: int = Field(...)
    role: ClubRole = ClubRole.MEMBER


class CreateClubMember(ClubMemberBase):
    """Lớp tạo ClubMember(Thành viên câu lạc bộ)"""


class MemberInfo(ClubMemberBase):
    """Lớp trả về Info thành viên(Thành viên câu lạc bộ)"""

    email: EmailStr
    joined_at: datetime | None = None
    role: ClubRole = ClubRole.MEMBER

    model_config = ConfigDict(from_attributes=True)


class ClubMemberData(BaseModel):
    """Lớp data trả về danh sách thành viên list"""

    id: int
    name: str
    description: str | None = None
    owner_id: int
    members: list[MemberInfo] = []

    model_config = ConfigDict(from_attributes=True)


class ClubMemberResponse(BaseModel):
    """Lớp trả về danh sách thành viên list"""

    status_code: int
    message: str | None = None
    data: ClubMemberData | None = []

    model_config = ConfigDict(from_attributes=True)


class ClubAddMemberResponse(BaseModel):
    """Lớp trả về khi thêm thành viên"""

    status_code: int
    message: str | None = None
    data: MemberInfo | None = []

    model_config = ConfigDict(from_attributes=True)
