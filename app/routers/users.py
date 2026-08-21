"""
app/routers/users.py
User endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.dependencies import RoleChecker, get_current_user
from app.models.user import SystemRole, User
from app.schemas.user import UserListResponse, UserResponse

router = APIRouter(prefix="/users", tags=["User"])

# Khởi tạo Type Alias
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
RequireAdmin = Annotated[User, Depends(RoleChecker([SystemRole.ADMIN]))]


@router.get(
    path="/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin cá nhân (không lộ password)",
)
def get_me(current_user: CurrentUser):
    """Lấy thông tin cá nhân"""
    return {
        "status_code": 200,
        "message": "Lấy thông tin thành công",
        "data": current_user,
    }


@router.get(
    path="",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm & lấy danh sách người dùng chỉ Admin",
)
def get_users(
    _: RequireAdmin,
    db: DbSession,
    q: Annotated[
        str | None,
        Query(description="Từ khóa tìm kiếm theo email hoặc full_name"),
    ] = None,
    is_active: Annotated[
        bool | None,
        Query(description="Lọc theo trạng thái tài khoản"),
    ] = None,
):
    """
    Danh sách/search người dùng (Chỉ cho Admin)
    """
    query = db.query(User)

    # Tìm kiếm theo từ khóa (email và full_name)
    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    # Lọc theo nếu có ghi
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.all()

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Lấy danh sách người dùng thành công",
        "data": users,
    }
