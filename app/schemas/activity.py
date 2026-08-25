"""
app/schemas/activity.py
Tạo Base/Create/Update/Response schema
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserShortResponse


class ActivityStatus(str, Enum):
    """Định nghĩa Enum Status"""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class ActivityPriority(str, Enum):
    """Định nghĩa Enum Priority"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActivityBase(BaseModel):
    """Tạo SchemaActivity cơ bản"""

    title: str = Field(
        ..., min_length=1, max_length=255, description="Tiêu đề hoạt động"
    )
    description: str | None = Field(default=None, description="Mô tả hoạt động")
    due_date: datetime | None = None
    priority: ActivityPriority = ActivityPriority.MEDIUM


class CreateActivity(ActivityBase):
    """Tạo mới POST"""

    assignee_id: int | None = Field(
        default=None, description="ID người được phân công (nếu có)"
    )


class UpdateActivity(BaseModel):
    """Lớp cập nhật (tất cả các trường đều là tùy chọn)"""

    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="Tiêu đề hoạt động"
    )
    description: str | None = Field(default=None, description="Mô tả hoạt động")
    due_date: datetime | None = None
    priority: ActivityPriority | None = None
    assignee_id: int | None = None


class ActivityResponseBase(ActivityBase):
    """Lớp trả về dữ liệu phẳng (Flat data)"""

    id: int
    club_id: int
    assignee_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityResponse(ActivityBase):
    """Lớp trả về hoạt động kèm thông tin User chi tiết (Nested)"""

    id: int
    club_id: int
    created_at: datetime | None = None
    assignee: UserShortResponse | None = None  

    model_config = ConfigDict(from_attributes=True)


class ActivityCreateResponse(BaseModel):
    """Lớp trả về khi tạo hd thành công"""

    status_code: int
    message: str
    data: ActivityResponseBase | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityListResponse(BaseModel):
    """Lớp trả về hoạt động danh sách"""

    status_code: int
    message: str
    data: list[ActivityResponseBase] = [] 

    model_config = ConfigDict(from_attributes=True)