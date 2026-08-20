"""
app/schemas/activity.py
Tạo Base/Create/Update/Response schema
"""

from datetime import datetime
from enum import Enum
from app.schemas.user import UserShortResponse

from pydantic import BaseModel, ConfigDict, Field


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
    status: ActivityStatus = ActivityStatus.TODO
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: datetime | None = None
    assignee_id: int | None = None


class CreateActivity(ActivityBase):
    """Tạo mới POST"""


class UpdateActivity(ActivityBase):
    """Lớp cập nhật"""


class DeleteActivity(ActivityBase):
    """Lớp xóa"""


class ActivityResponse(ActivityBase):
    """Lớp trả về"""

    id: int
    club_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    assignee: UserShortResponse | None

    model_config = ConfigDict(from_attributes=True)
