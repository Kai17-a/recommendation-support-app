from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.evaluations.schemas import EvaluationCreate, EvaluationUpdate
from app.infrastructure.models import Member, MemberEvaluation, ProjectExperience
from app.security.authorization import AccessControl


class EvaluationService:
    def __init__(self, session: Session, access: AccessControl | None = None) -> None:
        self.session = session
        self.access = access

    def list_for_member(self, member_id: UUID) -> list[MemberEvaluation]:
        self._member(member_id)
        return list(
            self.session.scalars(
                select(MemberEvaluation)
                .where(
                    MemberEvaluation.member_id == member_id, MemberEvaluation.deleted_at.is_(None)
                )
                .order_by(MemberEvaluation.evaluation_date.desc())
            )
        )

    def create(self, member_id: UUID, command: EvaluationCreate) -> MemberEvaluation:
        self._member(member_id)
        self._validate_project(member_id, command.project_experience_id)
        row = MemberEvaluation(member_id=member_id, **command.model_dump())
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def update(self, evaluation_id: UUID, command: EvaluationUpdate) -> MemberEvaluation:
        row = self._get(evaluation_id)
        self._validate_project(
            row.member_id,
            command.model_dump(exclude_unset=True).get(
                "project_experience_id", row.project_experience_id
            ),
        )
        for k, v in command.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        self.session.commit()
        self.session.refresh(row)
        return row

    def _validate_project(self, member_id: UUID, project_id: UUID | None) -> None:
        if project_id is None:
            return
        project = self.session.scalar(
            select(ProjectExperience).where(
                ProjectExperience.id == project_id,
                ProjectExperience.member_id == member_id,
                ProjectExperience.deleted_at.is_(None),
            )
        )
        if project is None:
            raise ApiError(
                status_code=422,
                code="VALIDATION_ERROR",
                message="指定された案件経験はメンバーに紐付きません。",
            )

    def delete(self, evaluation_id: UUID) -> None:
        row = self._get(evaluation_id)
        row.deleted_at = datetime.now(UTC)
        self.session.commit()

    def _member(self, member_id: UUID) -> Member:
        if self.access is not None:
            return self.access.ensure_member(member_id)
        row = self.session.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if row is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="メンバーが見つかりません。")
        return row

    def _get(self, evaluation_id: UUID) -> MemberEvaluation:
        row = self.session.scalar(
            select(MemberEvaluation).where(
                MemberEvaluation.id == evaluation_id, MemberEvaluation.deleted_at.is_(None)
            )
        )
        if row is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="人物評価が見つかりません。")
        self._member(row.member_id)
        return row
