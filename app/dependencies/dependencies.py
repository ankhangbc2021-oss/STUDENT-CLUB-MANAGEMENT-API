"""
app/dependencies/dependencies.py
"""

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db

# Models
from app.models.club import Club, ClubMember
from app.models.user import User

# Schemas
from app.schemas.club import ClubRole
from app.schemas.user import SystemRole

reusable_oauth2 = HTTPBearer()  # Đọc header Authrization(tự ktra resquest có gửi ko)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency cốt lõi: Giải mã JWT từ Header, kiểm tra tính toàn vẹn,
    và truy vấn thông tin User từ Database
    """

    # Tự lấy token nguyên bản
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        # Giải khóa token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")
        if not email:
            raise credentials_exception

    except jwt.ExpiredSignatureError as e:
        # Bắt lỗi token hết hạn
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except jwt.PyJWKError as e:
        # Bắt toàn bộ các lỗi còn lại: sai chữ ký,...
        raise credentials_exception from e

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại trong hệ thống!",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản này đã bị khóa hoặc ngừng sử dụng!",
        )

    return user


class RoleChecker:
    """
    Class Deependency dùng để phân quyền theo vai trò
    Nhận vào một list các role được phép truy cập

    Cách dùng trong endpoint:
        Depends(RoleChecker(["ADMIN"]))          # Chỉ admin
        Depends(RoleChecker(["ADMIN", "USER"]))  # admin hoặc user
    """

    def __init__(self, allowed_roles: list[SystemRole]):
        # Lưu danh sách role được phéo vô
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        # Lấy tên role
        user_role_name = current_user.role if current_user.role else None

        # Kiểm tra role có trong quyền ko

        if user_role_name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Quyền truy cập bị từ chối! "
                    f"Yêu cầu một trong các quyền: {self.allowed_roles!s}"
                ),
            )
        return current_user


class ClubRoleCheck:
    """
    Class ClubRoleCheck dùng để phân quyền vai tròng trong club
    Nhận vào list các role được phép truy cập

    Cách dùng trong endpoint:
        Depends(ClubRoleCheck("OWNER")) # Chỉ có owner
        Depends(ClubRoleCheck("OWNER", "MEMBER")) # owner và member
    """

    def __init__(self, *roles: ClubRole):
        self.allowed_roles = roles

    def __call__(
        self,
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> ClubMember:

        club_id = request.path_params.get("id") or request.path_params.get("club_id")
        if not club_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không tìm thất tham số id câu lạc bộ trên URL",
            )

        try:
            club_id = int(club_id)  # Tránh nhập số
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID câu lạc bộ không hợp lệ.",
            ) from e

        membership = (
            db.query(ClubMember)
            .filter(
                ClubMember.user_id == current_user.id,
                ClubMember.club_id == club_id,
            )
            .first()
        )
        existing_id = (
            db.query(Club)
            .filter(Club.id == club_id, Club.is_deleted.is_(False))
            .first()
        )

        # Nếu không có CLB trả về 404
        if not existing_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Câu lạc bộ không tồn tại trong hệ thống.",
            )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chưa tham gia câu lạc bộ này.",
            )

        # 4. Kiểm tra vai trò trong CLB
        user_role_str = membership.role
        allowed_roles_str = [str(r) for r in self.allowed_roles]

        if user_role_str not in allowed_roles_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Hành động yêu cầu một trong các quyền CLB: {allowed_roles_str}",
            )

        return membership
