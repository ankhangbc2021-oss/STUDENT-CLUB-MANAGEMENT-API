"""
app/db/seed.py

Tạo dữ liệu mẫu phục vụ test và demo
- Users
- Club
- Club Activities
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core import security
from app.db.database import Base, SessionLocal, engine

# import models
from app.models.activity import ClubActivity
from app.models.club import Club, ClubMember
from app.models.user import SystemRole, User

# import schemas
from app.schemas.activity import ActivityPriority, ActivityStatus
from app.schemas.club import ClubRole


def seed(db: Session) -> None:
    """Thêm dữ liệu"""

    # Kiểm tra có dữ liệu chưa
    if db.query(User).first():
        print("Dữ liệu đã tồn tại trong Database, đã dừng seed")
        return
    print("Đang tạo dữ liệu")

    # -----
    # SEED USERS (Mật khẩu mặc định cho tất cả là "123456")
    # -----

    default_password = security.hash_password("123456")

    admin_user = User(
        email="admin@gmail.com",
        password_hash=default_password,
        full_name="Quản Trị Viên",
        role=SystemRole.ADMIN,
        is_active=True,
    )

    user_owner = User(
        email="leader@gmail.com",
        password_hash=default_password,
        full_name="Nguyễn Văn Chủ Nhiệm",
        role=SystemRole.USER,
        is_active=True,
    )
    user_member = User(
        email="member@gmail.com",
        password_hash=default_password,
        full_name="Trần Thị Thành Viên",
        role=SystemRole.USER,
        is_active=True,
    )

    db.add_all([admin_user, user_owner, user_member])
    db.commit()
    db.refresh(admin_user)
    db.refresh(user_owner)
    db.refresh(user_member)

    # -----------
    # SEED CLUBS (Câu lạc bộ)
    # -----------

    club_it = Club(
        name="CLB Lập trình & AI",
        description="Nơi chia sẻ kiến thức về công nghệ, lập trình Web & AI",
        owner_id=user_owner.id,
    )
    club_music = Club(
        name="CLB Âm Nhạc",
        description="Giao lưu văn nghệ, đàn hát sinh viên",
        owner_id=user_owner.id,
    )

    db.add_all([club_it, club_music])
    db.commit()
    db.refresh(club_it)
    db.refresh(club_music)

    # ----------
    # SEED CLUB MEMBERS (Thành viên CLB)
    # ----------

    members = [
        # CLB IT
        ClubMember(club_id=club_it.id, user_id=user_owner.id, role=ClubRole.OWNER),
        ClubMember(club_id=club_it.id, user_id=user_member.id, role=ClubRole.MEMBER),
        # CLB Âm Nhạc
        ClubMember(club_id=club_music.id, user_id=user_owner.id, role=ClubRole.OWNER),
    ]

    db.add_all(members)
    db.commit()

    # ------------
    # SEED CLUB ACTIVITIES (Hoạt động / Task của CLB)
    # ------------
    activities = [
        ClubActivity(
            club_id=club_it.id,
            title="Tổ chức Workshop FastAPI cơ bản",
            description="Chuẩn bị slide, slide demo và phòng học trực tuyến",
            status=ActivityStatus.IN_PROGRESS,
            priority=ActivityPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=7),
            assignee_id=user_member.id,
        ),
        ClubActivity(
            club_id=club_it.id,
            title="Tuyển thành viên đợt 1",
            description="Lên bài truyền thông fanpage và form đăng ký",
            status=ActivityStatus.DONE,
            priority=ActivityPriority.MEDIUM,
            due_date=datetime.now(timezone.utc) - timedelta(days=2),
            assignee_id=user_owner.id,
        ),
        ClubActivity(
            club_id=club_it.id,
            title="Hackathon mùa Thu 2026",
            description="Tìm nhà tài trợ và lên thể lệ cuộc thi",
            status=ActivityStatus.TODO,
            priority=ActivityPriority.HIGH,
            due_date=datetime.now(timezone.utc) + timedelta(days=30),
            assignee_id=None,
        ),
    ]

    db.add_all(activities)
    db.commit()

    print("Seed dữ liệu mẫu thành công!")


if __name__ == "__main__":

    # Tự động tạo bảng nếu chưa tạo
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()

    try:
        seed(db_session)
    finally:
        db_session.close()
