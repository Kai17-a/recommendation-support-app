from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Department, Member, User, UserRole, UserStatus
from app.members.schemas import MemberCreate, MemberUpdate


class MemberService:
    """メンバーの業務データを扱うアプリケーションサービス。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self) -> list[Member]:
        statement = select(Member).where(Member.deleted_at.is_(None)).order_by(Member.name)
        return list(self.session.scalars(statement))

    def get_active(self, member_id: UUID) -> Member:
        member = self.session.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if member is None:
            raise self._not_found(member_id)
        return member

    def create(self, command: MemberCreate) -> Member:
        self._validate_references(command.department_id, command.manager_user_id)
        member = Member(**command.model_dump())
        self.session.add(member)
        self.session.commit()
        self.session.refresh(member)
        return member

    def update(self, member_id: UUID, command: MemberUpdate) -> Member:
        member = self.get_active(member_id)
        changes = command.model_dump(exclude_unset=True)
        department_id = changes.get("department_id", member.department_id)
        manager_user_id = changes.get("manager_user_id", member.manager_user_id)
        self._validate_references(department_id, manager_user_id)

        for field_name, value in changes.items():
            setattr(member, field_name, value)
        self.session.commit()
        self.session.refresh(member)
        return member

    def delete(self, member_id: UUID) -> None:
        member = self.get_active(member_id)
        member.deleted_at = datetime.now(UTC)
        self.session.commit()

    def restore(self, member_id: UUID) -> Member:
        member = self.session.get(Member, member_id)
        if member is None:
            raise self._not_found(member_id)
        if member.deleted_at is not None:
            member.deleted_at = None
            self.session.commit()
            self.session.refresh(member)
        return member

    def _validate_references(self, department_id: UUID, manager_user_id: UUID) -> None:
        department = self.session.get(Department, department_id)
        if department is None:
            raise ApiError(
                status_code=422,
                code="VALIDATION_ERROR",
                message="指定された部署が存在しません。",
                details={"department_id": str(department_id)},
            )

        manager = self.session.get(User, manager_user_id)
        if (
            manager is None
            or manager.role is not UserRole.MANAGER
            or manager.status is not UserStatus.ACTIVE
        ):
            raise ApiError(
                status_code=422,
                code="VALIDATION_ERROR",
                message="指定された管理者が有効なマネージャーではありません。",
                details={"manager_user_id": str(manager_user_id)},
            )

    @staticmethod
    def _not_found(member_id: UUID) -> ApiError:
        return ApiError(
            status_code=404,
            code="NOT_FOUND",
            message="メンバーが見つかりません。",
            details={"member_id": str(member_id)},
        )
