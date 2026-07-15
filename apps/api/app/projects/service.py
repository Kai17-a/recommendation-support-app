from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Member, ProjectExperience
from app.projects.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    """メンバー単位の案件経験を扱うアプリケーションサービス。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_member(self, member_id: UUID) -> list[ProjectExperience]:
        self._get_active_member(member_id)
        statement = (
            select(ProjectExperience)
            .where(
                ProjectExperience.member_id == member_id,
                ProjectExperience.deleted_at.is_(None),
            )
            .order_by(
                ProjectExperience.period_from.desc().nullslast(),
                ProjectExperience.project_name,
            )
        )
        return list(self.session.scalars(statement))

    def create(self, member_id: UUID, command: ProjectCreate) -> ProjectExperience:
        self._get_active_member(member_id)
        project = ProjectExperience(member_id=member_id, **command.model_dump())
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def get_active(self, project_id: UUID) -> ProjectExperience:
        project = self.session.scalar(
            select(ProjectExperience).where(
                ProjectExperience.id == project_id,
                ProjectExperience.deleted_at.is_(None),
            )
        )
        if project is None:
            raise self._not_found(project_id)
        return project

    def update(self, project_id: UUID, command: ProjectUpdate) -> ProjectExperience:
        project = self.get_active(project_id)
        changes = command.model_dump(exclude_unset=True)
        period_from = changes.get("period_from", project.period_from)
        period_to = changes.get("period_to", project.period_to)
        if period_from is not None and period_to is not None and period_to < period_from:
            raise ApiError(
                status_code=422,
                code="VALIDATION_ERROR",
                message="終了日は開始日以降にしてください。",
            )

        for field_name, value in changes.items():
            setattr(project, field_name, value)
        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: UUID) -> None:
        project = self.get_active(project_id)
        project.deleted_at = datetime.now(UTC)
        self.session.commit()

    def _get_active_member(self, member_id: UUID) -> Member:
        member = self.session.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if member is None:
            raise ApiError(
                status_code=404,
                code="NOT_FOUND",
                message="メンバーが見つかりません。",
                details={"member_id": str(member_id)},
            )
        return member

    @staticmethod
    def _not_found(project_id: UUID) -> ApiError:
        return ApiError(
            status_code=404,
            code="NOT_FOUND",
            message="案件経験が見つかりません。",
            details={"project_id": str(project_id)},
        )
