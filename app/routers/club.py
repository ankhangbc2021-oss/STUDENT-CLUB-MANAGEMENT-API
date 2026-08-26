"""
app/routers/club.py
Câu lạc bộ/Member/Activity endpoints
"""

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

# db
from app.db.database import get_db

# dependencies
from app.dependencies.dependencies import (
    ClubRoleCheck,
    RoleChecker,
    get_current_user,
)

# models
from app.models.activity_log import ActivityLog
from app.models.club import ClubMember
from app.models.user import SystemRole, User

# schemas
from app.schemas.activity import (
    ActivityCreateResponse,
    ActivityLimitOffsetResponse,
    ActivityPriority,
    ActivitySortField,
    ActivityStatus,
    CreateActivity,
    SortOrder,
)
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
from app.services import activity as activity_service
from app.services import club as club_service

# Chia router cho đẹp
router = APIRouter(prefix="/clubs", tags=["Club"])
router_log = APIRouter(prefix="/clubs", tags=["Club Log"])
router_member = APIRouter(prefix="/clubs", tags=["Club Member"])
router_activity = APIRouter(prefix="/clubs", tags=["Club Activity"])

# ---------------------------------------
# --------------- Log -------------------
# ---------------------------------------


@router_log.get(
    path="/log",
    response_model=ActivityLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy log (Chỉ ADMIN)",
)
def get_log(
    club_id: int | None = Query(default=None, description="Lọc theo CLB"),
    _: User = Depends(RoleChecker([SystemRole.ADMIN])),
    db: Session = Depends(get_db),
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


# Club
@router.post(
    path="",
    response_model=ClubResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo câu lạc bộ mới (Người tạo tự động thành OWNER)",
)
def create_new_club(
    club_in: CreateClub,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tạo câu lạc bộ mới:
    - Yêu cầu đăng nhập (JWT Bearer token)
    - Người tạo tự động gán OWNER
    - Tự động ghi nhận vào Activity Log
    """
    club_new = club_service.create_club(
        db=db, club_in=club_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": f"Tạo câu lạc bộ [{club_new.name}] thành công",
        "data": club_new,
    }


@router.get(
    path="",
    response_model=ClubResponseList,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách CLB của tôi (Thành viên)",
)
def get_my_clubs(
    search: str | None = Query(
        default=None, description="Tìm kiếm theo tên câu lạc bộ"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lấy danh sách CLB:
    - Yêu cầu xác thực tài khoản
    - Chỉ trả về CLB mà người hiện tại là OWNER hoặc MEMBER
    - Hỗ trợ tìm kiếm theo tên
    """
    get_clubs = club_service.get_user_clubs(
        db=db, current_user=current_user, search=search
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Lấy danh sách câu lạc bộ thành công",
        "data": get_clubs or [],
    }


@router.get(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy chi tiết CLB (thành viên)",
)
def get_club_detail(
    club_id: int = Path(..., description="ID của câu lạc bộ cần xem"),
    db: Session = Depends(get_db),
    _: ClubMember = Depends(ClubRoleCheck("OWNER", "MEMBER")),
):
    """
    Xem chi tiết CLB:
    - Bắt buộc đăng nhập
    - Trả về 404 nếu không tìm thấy CLB
    - Trả về 403 Forbidden nếu người dùng không thuộc CLB này
    """
    club_data = club_service.get_club_by_id(db=db, club_id=club_id)

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Lấy thông tin chi tiết câu lạc bộ có ID là: {club_id} thành công",
        "data": club_data,
    }


@router.put(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật CLB theo id (Chỉ cho OWNER)",
)
def update_club_by_id(
    club_in: UpdateClub,
    club_id: int = Path(..., description="ID của câu lạc bộ cần cập nhật"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: ClubMember = Depends(ClubRoleCheck("OWNER")),
):
    """
    Cập nhật CLB (Chỉ OWNER)
    """
    updated_club = club_service.update_club(
        db=db, club_id=club_id, club_in=club_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Cập nhật thành công",
        "data": updated_club,
    }


@router.delete(
    path="/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa CLB (Chỉ OWNER)",
)
def delete_club_by_id(
    club_id: int = Path(..., description="ID của CLB cần xóa (OWNER)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: ClubMember = Depends(ClubRoleCheck("OWNER")),
):
    """Xóa CLB (Soft delete hoặc Hard delete)"""
    club_service.delete_club(db=db, club_id=club_id, current_user=current_user)

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Xóa thành công",
        "data": None,
    }


# Member
@router_member.post(
    path="/{club_id}/members",
    response_model=ClubAddMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên mới (chỉ OWNER)",
)
def add_member(
    club_in: CreateClubMember,
    club_id: int = Path(..., description="Nhập ID của CLB để thêm thành viên"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: ClubMember = Depends(ClubRoleCheck("OWNER")),
):
    """Thêm thành viên mới vào CLB (Chỉ OWNER)"""
    new_member = club_service.add_membership(
        db=db, club_id=club_id, club_in=club_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": f"Thêm thành viên vào CLB thành công",
        "data": new_member,
    }


@router_member.delete(
    path="/{club_id}/members/{user_id}",
    response_model=ClubMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên của CLB (Không xóa được OWNER)",
)
def delete_member(
    club_id: int = Path(..., description="Nhập ID CLB cần xóa"),
    user_id: int = Path(..., description="Nhập ID người dùng cần xóa"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: ClubMember = Depends(ClubRoleCheck("OWNER")),
):
    """Xóa thành viên khỏi CLB"""
    club_service.delete_membership(
        db=db, club_id=club_id, user_id=user_id, current_user=current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Đã xóa thành công thành viên ID: {user_id}",
        "data": None,
    }


@router_member.get(
    path="/{club_id}/members",
    response_model=ClubMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách thành viên (Chỉ dành cho thành viên CLB)",
)
def get_members(
    club_id: int = Path(..., description="ID của câu lạc bộ cần xem"),
    db: Session = Depends(get_db),
    _: ClubMember = Depends(ClubRoleCheck("OWNER", "MEMBER")),
):
    """Lấy danh sách thành viên trong CLB"""
    members = club_service.get_members(db=db, club_id=club_id)

    return {
        "status_code": status.HTTP_200_OK,
        "message": f"Lấy danh sách thành viên câu lạc bộ ID {club_id} thành công",
        "data": members,
    }


@router.delete(
    path="/deleted/{club_id}",
    response_model=ClubResponse,
    status_code=status.HTTP_200_OK,
    summary="Xóa mềm CLB",
)
def soft_delete_club(
    club_id: int = Path(..., description="Nhập ID CLB để xóa mềm"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: ClubMember = Depends(ClubRoleCheck("OWNER")),
):
    """Xóa mềm CLB (đánh dấu is_deleted=True)"""
    club_service.is_deleted(db=db, club_id=club_id, current_user=current_user)

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Xóa mềm thành công",
        "data": None,
    }


# ---------------------------------------
# -------------- Activity ---------------
# ---------------------------------------


@router_activity.post(
    path="/{club_id}/activities",
    response_model=ActivityCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm hoạt động CLB (thành viên)",
)
def new_activity(
    activity_in: CreateActivity,
    club_id: int = Path(..., description="Nhập ID CLB để thêm hoạt động"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    membership: ClubMember = Depends(ClubRoleCheck("OWNER", "MEMBER")),
):
    """Tạo hoạt động mới cho CLB"""
    created_activity = activity_service.create_activity(
        db=db, club_id=club_id, activity_in=activity_in, current_user=current_user
    )

    return {
        "status_code": status.HTTP_201_CREATED,
        "message": "Tạo mới hoạt động thành công",
        "data": created_activity,
    }


@router_activity.get(
    path="/{club_id}/activities",
    response_model=ActivityLimitOffsetResponse,
    status_code=status.HTTP_200_OK,
    summary="Danh sách hoạt động CLB (Limit / Offset & Sort)",
)
def get_club_activities(
    club_id: int = Path(..., description="ID của câu lạc bộ"),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Số lượng bản ghi tối đa lấy về (1 - 100)",
    ),
    offset: int = Query(
        default=0, ge=0, description="Vị trí bắt đầu lấy bản ghi (bỏ qua N mục)"
    ),
    assignee: str | None = Query(
        default=None, description="Nhập ID của người được phân"
    ),
    search_title: str | None = Query(default=None, description="Nhập title cần tìm"),
    priority: ActivityPriority | None = Query(
        default=None, description="Lọc theo Priority (LOW/MEDIUM/HIGH)"
    ),
    status_filter: ActivityStatus | None = Query(
        default=None, description="Lọc theo Status (TODO/IN_PROGRESS/DONE)"
    ),
    sort_by: ActivitySortField = Query(
        default=ActivitySortField.CREATED_AT,
        description="Trường sắp xếp (created_at hoặc due_date)",
    ),
    order: SortOrder = Query(
        default=SortOrder.DESC,
        description="Thứ tự sắp xếp (asc: tăng dần, desc: giảm dần)",
    ),
    db: Session = Depends(get_db),
    _: User = Depends(ClubRoleCheck("OWNER", "MEMBER")),
):
    """
    Lấy danh sách hoạt động phân trang theo limit/offset:
    """
    result = activity_service.get_activity(
        db=db,
        club_id=club_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
        assignee=assignee,
        search_title=search_title,
        status_filter=status_filter,
        priority=priority,
    )

    return {
        "status_code": status.HTTP_200_OK,
        "message": "Lấy danh sách hoạt động thành công",
        "data": result,
    }
