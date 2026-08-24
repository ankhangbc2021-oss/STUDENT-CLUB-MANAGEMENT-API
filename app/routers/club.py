"""
app/routers/club.py
Câu lạc bộ/Member endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

# db
from app.db.database import get_db

# dependencies
from app.dependencies.dependencies import ClubRoleCheck

# models
from app.models.activity_log import ActivityLog
from app.models.club import ClubMember

# routers
from app.routers.users import CurrentUser, DbSession, RequireAdmin

# schemas
from app.schemas.activity_log import ActivityLogListResponse
from app.schemas.club import (
    ClubAddMemberResponse,
    ClubMemberResponse,
    ClubResponse,
    ClubResponseList,
    CreateClub,
    CreateClubMember,
    UpdateClub,
)

# services
from app.services import club as club_service

router = APIRouter(prefix="/clubs", tags=["Club"])

# Tạo Type Alias
RequireOwner = Annotated[ClubMember, Depends(ClubRoleCheck("OWNER"))]


# ---- Log ----
# Lấy log khi thêm xóa sửa...
@router.get(
    path="/log",
    response_model=ActivityLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy log (Chỉ ADMIN)",
)
def get_log(
    _: RequireAdmin,
    db: DbSession,
    club_id: Annotated[int | None, Query(description="Lọc theo CLB")] = None,
):
    """Lấy log ACTIVITY"""

    query = db.query(ActivityLog).order_by(ActivityLog.created_at.desc())

    if club_id:
        query = query.filter(ActivityLog.club_id == club_id)

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Lấy danh sách log thành công",
        "data": query.all(),
    }


# ---------------------------------------
# ---------- Club và Member -------------
# ---------------------------------------


# Tạo câu lạc bộ mới
@router.post(
    path="",
    response_model=ClubResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo câu lạc bộ mới (Người tạo tự động thành OWNER)",
)
def create_new_club(payload: CreateClub, db: DbSession, current_user: CurrentUser):
    """
    Tạo câu lạc bộ mới:
    - Yêu cầu đăng nhập (JWT Bearer token)
    - Người tạo tự động gán OWNER
    - Tự động ghi nhận vào Activity Log
    """

    club_new = club_service.create_club(
        db=db, club_in=payload, current_user=current_user
    )

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": f"Tạo câu lạc bộ [{club_new.name}] thành công",
        "data": club_new,
    }


# Lấy danh sách CLB
@router.get(
    path="",
    response_model=ClubResponseList,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách CLB của tôi (OWNER/MEMBER)",
)
def get_my_clubs(
    db: DbSession,
    current_user: CurrentUser,
    search: str | None = Query(None, description="Tìm kiếm theo tên câu lạc bộ"),
):
    """
    Lấy danh sách CLB
    - Yêu cầu xác thực tài khoản
    - Chỉ trả về CLB mà người hiện tại là OWNER hoặc MEMBER
    - Hỗ trợ tìm kiếm search
    """

    get_clubs = club_service.get_user_clubs(
        db=db, current_user=current_user, search=search
    )

    if not get_clubs:
        return {
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": f"Không tìm thấy tên CLB là: {search}",
            "data": [],
        }

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Lấy danh sách câu lạc bộ thành công",
        "data": get_clubs,
    }


# Xem chi tiết CLB
@router.get(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết CLB (Chỉ dành cho thành viên)",
)
def get_club_detail(
    db: DbSession,
    _: None = Depends(ClubRoleCheck("OWNER", "MEMBER")),
    club_id: int = Path(..., description="ID của câu lạc bộ cần xem"),
):
    """
    Xem chi tiết CLB:
    - Bắt buộc đăng nhập
    - Trả về 404 nếu không tìm thấy CLB
    - Trả về 403 Forbidden nếu người dùng không thuộc CLB này
    - Trả về thông tin CLB
    """
    club_data = club_service.get_club_by_id(db=db, club_id=club_id)

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Lấy thông tin chi tiết câu lạc bộ có ID là: {club_id} thành công",
        "data": club_data,
    }


# Cập nhật CLB
@router.put(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật CLB theo id (Chỉ cho OWNER và ADMIN)",
)
def update_club_by_id(
    db: DbSession,
    club_in: UpdateClub,
    current_user: CurrentUser,
    _: RequireOwner,
    club_id: int = Path(..., description="ID của câu lạc bộ cần cập nhật"),
):
    """
    Cập nhật CLB (ADMIN luôn được qua)
    - Nhận vào id của CLB
    - Kiểm tra CLB có tồn tại không
    """

    update_club = club_service.update_club(
        db=db, club_id=club_id, club_in=club_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Cập nhật thành công",
        "data": update_club,
    }


# Xóa CLB
@router.delete(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa CLB (Chỉ OWNER và ADMIN)",
)
def delete_club_by_id(
    db: DbSession,
    current_user: CurrentUser,
    _: RequireOwner,
    club_id: int = Path(..., description="ID của CLB cần xóa (OWNER)"),
):
    """
    Xóa CLB (ADMIN luôn được qua)
    - Nhập ID của CLB
    - Kiểm tra CLB có tồn tại không, nếu không trả về 404
    - Trả về thông báo xóa thành công
    """

    club_service.delete_club(db=db, club_id=club_id, current_user=current_user)

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Xóa thành công",
        "data": None,
    }


# Thêm thành viên
@router.post(
    path="/{club_id}/members",
    response_model=ClubAddMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên mới (chỉ OWNER)",
)
def add_member(
    db: DbSession,
    current_user: CurrentUser,
    _: RequireOwner,
    club_in: CreateClubMember,
    club_id: int = Path(..., description="Nhập ID của CLB để thêm thành viên"),
):
    """
    Thêm thành viên (Chỉ OWNER) (ADMIN luôn được qua)
    - Nhập ID của CLB
    - Kiểm tra CLB có tồn tại không
    - Nhập thông tin cần thêm
    - Trả về thông báo thêm thành công
    """

    new_member = club_service.add_membership(
        db=db, club_id=club_id, club_in=club_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": f"Thêm thành viên có ID: {current_user.id} vào CLB thành công",
        "data": new_member,
    }


# Xóa thành viên
@router.delete(
    path="/{club_id}/members/{user_id}",
    response_model=ClubMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên của CLB (Không xóa được OWNER chỉ xóa được MEMBER)",
)
def delete_member(
    db: DbSession,
    _: RequireOwner,
    current_user: CurrentUser,
    club_id: int = Path(..., description="Nhập ID CLB cần xóa"),
    user_id: int = Path(..., description="Nhập ID người dùng cần xóa"),
):
    """
    Xóa thành viên
    - Nhận ID của CLB
    - Nhập ID của người dùng
    - Kiểm tra CLB và người dùng có tồn tại không
    - Kiểm tra CLB có thành viên này không
    """

    club_service.delete_membership(
        db=db, club_id=club_id, user_id=user_id, current_user=current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Đã xóa thành công thành viên ID là: {user_id}",
        "data": None,
    }


# Lấy danh sách thành viên
@router.get(
    path="/{club_id}/members",
    response_model=ClubMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành viên (Chỉ dành cho thành viên)",
)
def get_members(
    db: DbSession,
    _: None = Depends(ClubRoleCheck("OWNER", "MEMBER")),
    club_id: int = Path(..., description="ID của câu lạc bộ cần xem"),
):
    """
    Xem danh sách thành viên CLB
    - Bắt buộc đăng nhập
    - Trả về 404 nếu không tìm thấy CLB
    - Trả về 403 Forbidden nếu người dùng không thuộc CLB này
    - Trả về thông tin CLB kèm danh sách thành viên nếu hợp lệ
    """
    club_member = club_service.get_members(db=db, club_id=club_id)

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Lấy danh sách thành viên câu lạc bộ có ID là: {club_id} thành công",
        "data": club_member,
    }


# Xóa mềm CLB
@router.delete(
    path="/deleted/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa CLB mền (vẫn có trong DB)",
)
def is_deleted(
    db: DbSession,
    current_user: CurrentUser,
    _: RequireOwner,
    club_id: int = Path(..., description="Nhập ID CLB để xóa mền"),
):
    """Xóa CLB mềm"""

    club_service.is_deleted(db=db, club_id=club_id, current_user=current_user)
    
    return {
        "status_code": status.HTTP_200_OK,
        "message": "Xóa mềm thành công",
        "data": None,
    }
