from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Member, UserRole
from app.security.authentication import CurrentUser


class AccessControl:
    """操作者の役割と所属部署から業務データのアクセス範囲を決定する。"""

    def __init__(self, session: Session, user: CurrentUser) -> None:
        self.session = session
        self.user = user

    def member_scope(self):
        self.require_manager()
        return or_(
            Member.manager_user_id == self.user.id,
            Member.department_id == self.user.department_id,
        )

    def ensure_member(self, member_id: UUID, *, include_deleted: bool = False) -> Member:
        statement = select(Member).where(Member.id == member_id, self.member_scope())
        if not include_deleted:
            statement = statement.where(Member.deleted_at.is_(None))
        member = self.session.scalar(statement)
        if member is None:
            raise self._forbidden()
        return member

    def ensure_department(self, department_id: UUID) -> None:
        self.require_manager()
        if department_id != self.user.department_id:
            raise self._forbidden()

    def require_manager(self) -> None:
        if self.user.role is not UserRole.MANAGER:
            raise self._forbidden()

    def require_system_operator(self) -> None:
        if self.user.role is not UserRole.SYSTEM_OPERATOR:
            raise self._forbidden()

    @staticmethod
    def _forbidden() -> ApiError:
        return ApiError(
            status_code=403,
            code="FORBIDDEN",
            message="このリソースを操作する権限がありません。",
        )
