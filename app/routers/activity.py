"""
app/routers/activity.py
Hoạt động câu lạc bộ endpoints
"""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

# db
from app.db.database import get_db

# dependencies
from app.dependencies.dependencies import get_current_user

# model
from app.models.user import User

# schemas
from app.schemas.activity import (
    ActivityDetailResponse,
    UpdateActivity,
)

# services
from app.services import activity as activity_services

router = APIRouter(prefix="/activities", tags=["Club Activity"])


@router.get(
    path="/{activity_id}",
    response_model=ActivityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết hoạt động của CLB (Thành viên)",
)
def get_acivitis_deltail(
    activity_id: int = Path(
        ..., description="Nhập ID của hoạt động cần xem chi tiết hoạt động"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lấy chi tiết hoạt động của CLB
    - Nhận ID của CLB
    - Trả về
    """

    activity = activity_services.get_activity_deltail(
        db=db, activity_id=activity_id, current_user=current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Lấy thành công hoạt động chi tiết CLB có ID: {activity_id}",
        "data": activity,
    }


@router.put(
    path="/{activity_id}",
    response_model=ActivityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật hoạt động CLB (OWNER, assignee_id(Người được phân))",
)
def put_update_activity(
    activity_id: int = Path(..., description="Nhập ID hoạt động cần cập nhật"),
    activity_in: UpdateActivity = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cập nhật các trường hợp lệ, không ghi đè các trường không gửi lên:
    - Hỗ trợ cập nhật title, description, due_date, priority, status, assignee_id
    - Tự động validate quyền và workflow trạng thái
    """
    updated_act = activity_services.update_activity(
        db=db,
        activity_id=activity_id,
        activity_in=activity_in,
        current_user=current_user,
    )
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Cập nhật hoạt động thành công",
        "data": updated_act,
    }


@router.delete(
    path="/{activity_id}",
    response_model=ActivityDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa hoạt động CLB (OWNER)",
)
def delete_activity(
    activity_id: int = Path(..., description="ID hoạt động của CLB cần xóa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Xóa hoạt động:
    - Bắt buộc kiểm tra quyền ( Owner)
    - Trả về response chuẩn dạng bọc
    """
    activity_services.delete_activity(
        db=db, activity_id=activity_id, current_user=current_user
    )
    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Xóa thành công hoạt động có ID: {activity_id}",
        "data": None,
    }
