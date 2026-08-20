"""
app/schemas/user.py
Tạo Base/Create/Update/Response schema
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SystemRole(str, Enum):
    """Định nghĩ Enum Role hệ thống (USER / ADMIN)"""

    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    """Lớp cơ bản"""

    email: EmailStr = Field(...)


class UserCreate(UserBase):
    """Lớp tạo người dùng"""

    full_name: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role: SystemRole = SystemRole.USER


class UserUpdate(UserBase):
    """Lớp cập nhật người dùng"""

    full_name: str = Field(..., min_length=1)
    password_hash: str = Field(..., min_length=1)
    is_active: bool = True


class UserLogin(UserBase):
    """Lớp nhận dữ liệu đăng nhập"""

    password_hash: str = Field(..., min_length=1)


class UserResponse(UserBase):
    """Lớp trả về cho client"""

    id: int
    full_name: str | None = None
    is_active: bool = True

    role: SystemRole = SystemRole.USER
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserShortResponse(UserBase):
    """Lớp bổ trợ cho clubmember"""

    id: int
    full_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
