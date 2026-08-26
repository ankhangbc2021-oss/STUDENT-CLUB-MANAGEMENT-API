"""
app/services/club.py
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

# models
from app.models.activity_log import ActivityAction
from app.models.club import Club, ClubMember
from app.models.user import User

# schemas
from app.schemas.club import (  # OWNER / MEMBER
    ClubRole,
    CreateClub,
    CreateClubMember,
    UpdateClub,
)
from app.services.activity_log import log_activity


# Liên quan tới CLB
def create_club(db: Session, club_in: CreateClub, current_user: User) -> Club:
    """Tạo CLB mới"""

    # Kiểm tra tên clb xem có trùng không
    # Dùng func.lower(Club.name) để SQL tự chuyển về chữ thường khi so sánh
    existing_club = (
        db.query(Club)
        .filter(func.lower(Club.name) == club_in.name.lower().strip())
        .first()
    )
    if existing_club:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên câu lạc bộ đã tồn tại, vui lòng chọn tên khác",
        )
    # tạo câu lạc bộ
    new_club = Club(
        name=club_in.name,
        description=club_in.description,
        owner_id=current_user.id,
    )

    db.add(new_club)
    db.flush()  # Flush để lấy new_club.id trước khi commit

    # Tự thêm người tạo làm thành viên mới cho clb
    membership = ClubMember(
        club_id=new_club.id,
        user_id=current_user.id,
        role=ClubRole.OWNER,
    )
    db.add(membership)

    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=new_club.id,
        action=ActivityAction.CREATE_CLUB,
        description=(
            f"User {current_user.email} đã tạo câu lạc bộ "
            f"{new_club.name} và trở thành OWNER"
        ),
    )
    db.commit()
    db.refresh(new_club)
    db.refresh(membership)

    return new_club


def get_user_clubs(
    db: Session,
    current_user: User,
    search: str | None = None,
) -> list[dict]:
    """Lấy danh sách CLB (TV)"""

    # Query kết hợp Club và ClubMember dựa theo user_id
    query = (
        db.query(
            Club.id,
            Club.name,
            Club.description,
            Club.owner_id,
            Club.created_at,
            ClubMember.role.label("user_role"),  # tương đương với từ khóa AS tên_mới
        )
        .join(ClubMember, Club.id == ClubMember.club_id)
        .filter(
            or_(ClubMember.user_id == current_user.id, current_user.role == "ADMIN")
        )
    )

    if not query.all():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bạn chưa gia nhập CLB nào"
        )

    # Nếu tìm kiếm
    if search:
        search_kw = f"%{search.strip()}%"
        query = query.filter(Club.name.ilike(search_kw))

    # Sắp xếp mới nhất
    results = query.order_by(Club.created_at.desc()).all()

    return results


def get_club_by_id(db: Session, club_id: int) -> dict:
    """Tìm chi tiết câu lạc bộ theo ID"""

    # Tìm câu lạc bộ
    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Câu lạc bộ không tồn tại"
        )

    return club


def update_club(
    db: Session,
    club_id: int,
    club_in: UpdateClub,
    current_user: User,
) -> Club:
    """Cập nhật club theo id"""
    # Kiểm tra có id club ko
    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Câu lạc bộ không tồn tại"
        )

    # Kiểm tra tên có trùng tên cũ không
    if club_in.name and club_in.name.strip().lower() != club.name.lower():
        existing = (
            db.query(Club)
            .filter(func.lower(Club.name) == club_in.name.strip().lower())
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên câu lạc bộ này đã được sử dụng",
            )

        club.name = club_in.name.strip()

    if club_in.description is not None:
        club.description = club_in.description.strip()

    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=club_id,
        action=ActivityAction.UPDATE_CLUB,
        description=f"User {current_user.email} đã cập nhật thông tin câu lạc bộ '{club.name}'.",
    )

    db.commit()
    db.refresh(club)
    return club


def delete_club(db: Session, club_id: int, current_user: User):
    """Xóa club theo id"""

    club = db.query(Club).filter(Club.id == club_id).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Câu lạc bộ không tồn tại"
        )

    club_name = club.name

    # Xóa club liên quan
    db.query(ClubMember).filter(ClubMember.club_id == club_id).delete()

    # Xóa clb
    db.delete(club)

    # Ghi log
    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=club_id,
        action=ActivityAction.DELETE_CLUB,
        description=f"User {current_user.email} đã xóa câu lạc bộ '{club_name}.'",
    )

    # Lưu
    db.commit()


def is_deleted(db: Session, club_id: int, current_user: User):
    """Xóa mềm CLB (OWNER)"""

    # Lấy CLB chưa bị xóa mềm
    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ không tồn tại hoặc đã bị xóa",
        )

    club.is_deleted = True
    club.deleted_at = datetime.now(timezone.utc)

    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=club_id,
        action=ActivityAction.DELETE_CLUB,
        description=f"User {current_user.email} đã xóa(mềm) câu lạc bộ '{club.name}'",
    )

    db.commit()

    return club


# Liên quan tới thành viên CLB
def add_membership(
    db: Session,
    club_id: int,
    club_in: CreateClubMember,
    current_user: User,
) -> ClubMember:
    """Thêm thành viên (chỉ owner mới thêm được)"""

    # Tìm User
    target_user = db.query(User).filter(User.id == club_in.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại"
        )

    existing_id = db.query(Club).filter(Club.id == club_id).first()

    # Nếu không có CLB trả về 404
    if not existing_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Câu lạc bộ không tồn tại trong hệ thống",
        )

    # Kiểm tra người dùng tồn tại trong CLB chưa
    existing = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == club_in.user_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID: {club_in.user_id} đã là thành viên của CLB có ID: {club_id}",
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=club_id,
        action=ActivityAction.ADD_MEMBER,
        description=(
            f"User {current_user.email} đã thêm '{target_user.email}' vào CLB",
        ),
    )

    new_member = ClubMember(
        club_id=club_id,
        user_id=club_in.user_id,
        role=ClubRole.MEMBER,
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return {
        "user_id": new_member.user_id,
        "email": target_user.email,
        "full_name": target_user.full_name,
        "role": new_member.role,
        "joined_at": new_member.joined_at,
    }


def delete_membership(
    db: Session,
    club_id: int,
    user_id: int,
    current_user: User,
):
    """Xóa thành viên CLB (OWNER)"""

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại"
        )

    existing_club = db.query(Club).filter(Club.id == club_id).first()
    if not existing_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Câu lạc bộ không tồn tại!"
        )

    club_member = (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id)
        .first()
    )

    # Kiểm tra có thành viên trong CLB
    if not club_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CLB {existing_club.name} không có thành viên có ID là: {user_id}",
        )

    # Kiểm tra role
    if club_member.role == ClubRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID: {user_id} là OWNER không thể xóa khỏi CLB",
        )

    # Viết log
    log_activity(
        db=db,
        user_id=current_user.id,
        club_id=club_id,
        action=ActivityAction.REMOVE_MEMBER,
        description=f"User {current_user.email} đã xóa thành viên ID: {user_id} khỏi CLB",
    )

    db.delete(club_member)
    db.commit()

    return club_member


def get_members(db: Session, club_id: int):
    """Lấy danh sách member"""
    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Câu lạc bộ không tồn tại"
        )

    members_query = (
        db.query(
            ClubMember.user_id,
            ClubMember.role,
            ClubMember.joined_at,
            User.email,
            User.full_name,
        )
        .join(User, ClubMember.user_id == User.id)
        .filter(ClubMember.club_id == club_id)
        .all()
    )

    member_list = [
        {
            "user_id": m.user_id,
            "email": m.email,
            "full_name": m.full_name,
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m in members_query
    ]

    return {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "owner_id": club.owner_id,
        "created_at": club.created_at,
        "members": member_list,
    }
