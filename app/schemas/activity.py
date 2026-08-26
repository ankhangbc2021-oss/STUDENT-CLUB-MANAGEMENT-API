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


#  ----- Limit/offset -------


class ActivitySortField(str, Enum):
    """Lớp để lọc theo ngày tạo/ngày hạn xử lý"""

    CREATED_AT = "created_at"
    DUE_DATE = "due_date"


class SortOrder(str, Enum):
    """Lớp để trả về tăng dần hoặc giảm dần"""

    ASC = "asc"
    DESC = "desc"


# ---------


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


class ActivityResponseBase(ActivityBase):
    """Lớp trả về dữ liệu phẳng (Flat data)"""

    id: int
    club_id: int
    assignee_id: int | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ActivityCreateResponse(BaseModel):
    """Lớp trả về khi tạo hd thành công"""

    status_code: int
    message: str
    data: ActivityResponseBase | None = []

    model_config = ConfigDict(from_attributes=True)


class ActivityListResponse(BaseModel):
    """Lớp trả về hoạt động danh sách"""

    status_code: int
    message: str
    data: list[ActivityResponseBase] | None = []

    model_config = ConfigDict(from_attributes=True)


class ActivityDetailResponse(BaseModel):
    """Lớp trả về chi tiết hoạt động"""

    status_code: int
    message: str
    data: ActivityResponseBase | None = []

    model_config = ConfigDict(from_attributes=True)


class ActivityResponseData(BaseModel):
    """Lớp trả về chi tiết"""

    id: int
    club_id: int
    assignee_id: int | None = None
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: ActivityPriority
    status: ActivityStatus
    created_at: datetime
    assignee: UserShortResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Resquest -----
class UpdateActivity(BaseModel):
    """Lớp cập nhật (tất cả các trường đều là tùy chọn)"""

    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="Tiêu đề hoạt động"
    )
    description: str | None = Field(default=None, description="Mô tả hoạt động")
    due_date: datetime | None = None
    priority: ActivityPriority | None = (
        Field(default=None, description="Mức độ ưu tiên"),
    )
    status: ActivityStatus | None = Field(default=None, description="Trạng thái")
    assignee_id: int | None = Field(
        default=None, description="ID thành viên CLB được phân công"
    )


class AssignActivity(BaseModel):
    """Lớp phân công thành viên"""

    assignee_id: int | None = Field(
        ...,
        description="ID thành viên được giao việc (hoặc null nếu hủy phân công)",
    )


# class UpdateStatus(BaseModel):
#     """Lớp cập nhật status"""

#     status: ActivityStatus = Field(
#         ...,
#         description="Trạng thái mới (TODO, IN_PROGRESS, DONE)",
#         examples=["IN_PROGRESS"],
#     )


# Limit/Offset


class LimitOffsetMeta(BaseModel):
    """Lớp trả về dữ liệu phân trang"""

    limit: int = Field(..., description="Số lượng bản ghi tối đa lấy về")
    offset: int = Field(..., description="Vị trí bản ghi bắt đầu bỏ qua")
    total: int = Field(..., description="Tổng số bản ghi thỏa mãn điều kiện")
    has_more: bool = Field(..., description="Còn dữ liệu ở phía sau hay không")


class ActivityLimitOffsetData(BaseModel):
    """Lớp trả về danh sách hoạt động"""

    items: list[ActivityResponseData]
    pagination: LimitOffsetMeta

    model_config = ConfigDict(from_attributes=True)


class ActivityLimitOffsetResponse(BaseModel):
    """Lớp trả về khi phân trang thành công"""

    status_code: int
    message: str
    data: ActivityLimitOffsetData

    model_config = ConfigDict(from_attributes=True)
