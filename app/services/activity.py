"""app/services/activity.py"""

from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

# models
from app.models.activity import ClubActivity
from app.models.club import Club, ClubMember
from app.models.user import SystemRole, User

# schemas
from app.schemas.activity import (
    ActivityPriority,
    ActivitySortField,
    ActivityStatus,
    AssignActivity,
    CreateActivity,
    SortOrder,
    UpdateActivity,
)
from app.schemas.club import ClubRole

# Ma trận chuyển đổi trạng thái workflow hợp lệ
VALID_STATUS_TRANSITIONS = {
    ActivityStatus.TODO: [ActivityStatus.IN_PROGRESS],
    ActivityStatus.IN_PROGRESS: [ActivityStatus.DONE, ActivityStatus.TODO],
    ActivityStatus.DONE: [ActivityStatus.TODO],  # Chỉ OWNER/ADMIN được phép mở lại
}


def _get_activity_and_verify_access(
    db: Session, activity_id: int, current_user: User
) -> tuple[ClubActivity, ClubMember | None]:
    """
    Tìm hoạt động và kiểm tra user có quyền truy cập CLB chứa hoạt động hay không

    Return:
        - activity: Hoạt động CLB
        - membership: Thành viên CLB
    """

    activity = db.query(ClubActivity).filter(ClubActivity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy hoạt động có ID: {activity_id}",
        )

    club = (
        db.query(Club)
        .filter(Club.id == activity.club_id, Club.is_deleted.is_(False))
        .first()
    )
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ chứa hoạt động này không tồn tại hoặc đã bị xóa.",
        )

    membership = None
    if current_user.role != SystemRole.ADMIN:
        membership = (
            db.query(ClubMember)
            .filter(
                ClubMember.club_id == activity.club_id,
                ClubMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không phải là thành viên của câu lạc bộ này.",
            )

    return activity, membership


def _validate_assignee(db: Session, club_id: int, assignee_id: int | None) -> None:
    """Kiểm tra assignee_id có thuộc thành viên đang sinh hoạt trong CLB hay không"""
    if assignee_id is not None:
        target_member = (
            db.query(ClubMember)
            .filter(
                ClubMember.club_id == club_id,
                ClubMember.user_id == assignee_id,
            )
            .first()
        )
        if not target_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Người dùng ID {assignee_id} "
                    "không phải là thành viên trong câu lạc bộ.",
                ),
            )


def create_activity(
    db: Session, club_id: int, activity_in: CreateActivity
) -> ClubActivity:
    """Tạo hoạt động cho CLB (Thành viên)"""

    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cậu lạc bộ không tồn tại trong hệ thống hoặc đã bị xóa",
        )

    new_activity = ClubActivity(
        club_id=club_id,
        title=activity_in.title,
        description=activity_in.description,
        due_date=activity_in.due_date,
        priority=activity_in.priority,
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


def get_activity(
    db: Session,
    club_id: int,
    limit: int = 10,
    offset: int = 0,
    sort_by: ActivitySortField = ActivitySortField.CREATED_AT,
    order: SortOrder = SortOrder.DESC,
    assignee: int | None = None,
    search_title: str | None = None,
    status_filter: ActivityStatus | None = None,
    priority: ActivityPriority | None = None,
) -> dict:
    """
    Lấy danh sách hoạt động CLB (TV)
    List/filter/search hoạt động câu lạc bộ
    """

    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ không tồn tại hoặc đã bị xóa mềm",
        )

    query = db.query(ClubActivity).filter(ClubActivity.club_id == club_id)

    # Nếu nhập tiến độ
    if priority is not None:
        query = query.filter(ClubActivity.priority == priority)

    # Nếu nhập ID người được phân
    if assignee is not None:
        query = query.filter(ClubActivity.assignee_id == assignee)

    # Nếu tìm theo title
    if search_title is not None:
        search_title_kw = f"%{search_title.strip()}%"
        query = query.filter(ClubActivity.title.ilike(search_title_kw))

    # Tìm theo status
    if status_filter is not None:
        query = query.filter(ClubActivity.status == status_filter)

    total = query.count()  # Đếm tổng bản ghi

    # sort linh hoạt
    sort_column = (
        ClubActivity.due_date
        if sort_by == ActivitySortField.DUE_DATE
        else ClubActivity.created_at
    )

    # Nếu tăng dần
    if order == SortOrder.ASC:
        ordered_col = (
            asc(sort_column).nulls_last()
            if sort_by == ActivitySortField.DUE_DATE
            else asc(sort_column)
        )
    else:
        ordered_col = (
            desc(sort_column).nulls_last()
            if sort_by == ActivitySortField.DUE_DATE
            else desc(sort_column)
        )

    # Truy vấn với LIMIT và OFFSET
    items = query.order_by(ordered_col).offset(offset).limit(limit).all()

    # Còn bản ghi tiếp theo ko
    has_more = (offset + limit) < total

    return {
        "items": items,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": has_more,
        },
    }


def get_activity_deltail(
    db: Session, activity_id: int, current_user: User
) -> ClubActivity:
    """
    Lấy chi tiết hoạt động câu lạc bộ
    """

    activity, membership = _get_activity_and_verify_access(
        db=db, activity_id=activity_id, current_user=current_user
    )

    return activity


def update_activity(
    db: Session, activity_id: int, activity_in: UpdateActivity, current_user: User
):
    """Cập nhật hoạt động CLB (OWNER/ADMIN/assignee_id)"""

    activity, membership = _get_activity_and_verify_access(
        db=db, activity_id=activity_id, current_user=current_user
    )

    # Kiểm tra người dùng
    is_admin = current_user.role == SystemRole.ADMIN
    is_owner = membership.role == ClubRole.OWNER
    is_assignee = activity.assignee_id == current_user.id
    # print(1==1)
    # Kiểm tra quyền thao tác
    if not (is_admin or is_owner or is_assignee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền chỉnh sửa hoạt động này.",
        )

    # Lấy dữ liệu chỉ gồm các trường được truyền lên (không ghi đè trường bị bỏ qua)
    update_data = activity_in.model_dump(exclude_unset=True)

    if not update_data:
        return activity

    # Kiểm tra assignee_id có cập nhật ko
    if "assignee_id" in update_data:
        _validate_assignee(
            db=db, club_id=activity.club_id, assignee_id=update_data["assignee_id"]
        )

    # Kiểm tra nếu có cập nhật status
    if "status" in update_data and update_data["status"] != activity.status:
        new_status = update_data["status"]
        old_status = activity.status

        allowed_transitions = VALID_STATUS_TRANSITIONS.get(old_status, [])

        if new_status not in allowed_transitions and not (is_admin or is_owner):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Không thể chuyển workflow từ '{old_status}' sang '{new_status}'",
            )

        # Chỉ OWNER hoặc ADMIN mới lặp lại từ DONE -> TODO
        if (
            old_status == ActivityStatus.DONE
            and new_status == ActivityStatus.TODO
            and not (is_admin or is_owner)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ Ban Quản Trị (OWNER/ADMIN) mới được mở lại hoạt động đã hoàn thành.",
            )

    # Gán giá trị vào Model hoạt động
    for name, value in update_data.items():
        setattr(activity, name, value)

    db.commit()
    db.refresh(activity)
    return activity


def delete_activity(
    db: Session,
    activity_id: int,
    current_user: User,
) -> None:
    """Xóa hoạt động CLB (OWNER/ADMIN)"""

    activity, membership = _get_activity_and_verify_access(
        db=db, activity_id=activity_id, current_user=current_user
    )

    is_admin = current_user.role == SystemRole.ADMIN
    is_owner = membership and membership.role == ClubRole.OWNER

    # Chỉ Owner hoặc Admin mới xóa được

    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa hoạt động này",
        )

    db.delete(activity)  # Xóa
    db.commit()


def assign_activity_member(
    db: Session, activity_id: int, activity_in: AssignActivity, current_user: User
) -> ClubActivity:
    """Phân công viêc cho thành viên (Admin hoặc Owner)"""

    activity, membership = _get_activity_and_verify_access(
        db=db, activity_id=activity_id, current_user=current_user
    )

    is_admin = current_user.role == SystemRole.ADMIN
    is_owner = membership and membership.role == ClubRole.OWNER

    if not (is_admin or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền phân công người khác",
        )

    # Kiểm tra người phân công có phải thuộc CLB ko
    _validate_assignee(
        db=db, club_id=activity.club_id, assignee_id=activity_in.assignee_id
    )

    activity.assignee_id = activity_in.assignee_id

    db.commit()
    db.refresh(activity)
    return activity
