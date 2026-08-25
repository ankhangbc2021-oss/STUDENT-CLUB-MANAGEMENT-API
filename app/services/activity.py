"""app/services/activity.py"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# models
from app.models.activity import ClubActivity
from app.models.club import Club
from app.models.user import User

# schemas
from app.schemas.activity import (
    ActivityPriority,
    ActivityStatus,
    CreateActivity,
    UpdateActivity,
)


def create_activity(
    db: Session, activity_id: int, activity_in: CreateActivity
) -> ClubActivity:
    """Tạo hoạt động cho CLB (Thành viên)"""

    club = (
        db.query(Club)
        .filter(Club.id == activity_id, Club.is_deleted.is_(False))
        .first()
    )

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cậu lạc bộ không tồn tại trong hệ thống",
        )

    new_activity = ClubActivity(
        club_id=activity_id,
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
    activity_id: int,
    priority: ActivityPriority = None,
) -> list[ClubActivity]:
    """
    Lấy danh sách hoạt động CLB (TV)
    List/filter/search hoạt động câu lạc bộ
    """

    club = (
        db.query(Club)
        .filter(Club.id == activity_id, Club.is_deleted.is_(False))
        .first()
    )

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ không tồn tại hoặc đã bị xóa mềm",
        )

    query = db.query(ClubActivity).filter(ClubActivity.club_id == activity_id)

    if priority is not None:
        query = query.filter(ClubActivity.priority == priority)

    results = query.order_by(ClubActivity.created_at.desc()).all()

    return results
