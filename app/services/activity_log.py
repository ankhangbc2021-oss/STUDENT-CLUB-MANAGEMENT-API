"""
app/services/activity_log.py
Xử lý log
"""

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityAction, ActivityLog


def log_activity(
    db: Session,
    user_id: int,
    club_id: int,
    action: ActivityAction,
    description: str | None = None,
) -> ActivityLog:
    """Hàm phụ trợ trự động ghi log vào bảng"""

    log_entry = ActivityLog(
        user_id=user_id,
        club_id=club_id,
        action=action,
        description=description,
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return log_entry
