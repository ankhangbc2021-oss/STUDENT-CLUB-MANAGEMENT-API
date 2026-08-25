"""
app/schemas/activity_log.py
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityLogBase(BaseModel):
    """Lớp cơ bản cho log"""

    id: int
    user_id: int | None = None
    club_id: int | None = None
    action: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityLogListResponse(BaseModel):
    """Lớp trả về theo dạng cơ bản"""

    status_code: int = 200
    message: str
    data: list[ActivityLogBase] | None = []
