from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.dispatcher import RecommendationGenerationDispatcher
from app.core.errors import ApiError
from app.infrastructure.models import (
    AiJob,
    Member,
    Recommendation,
    RecommendationEvidence,
    RecommendationVersion,
)
from app.recommendations.schemas import (
    RecommendationCreate,
    RecommendationFinalize,
    RecommendationUpdate,
    RecommendationVersionUpdate,
)
from app.security.authorization import AccessControl


class RecommendationService:
    def __init__(
        self,
        s: Session,
        dispatcher: RecommendationGenerationDispatcher | None = None,
        access: AccessControl | None = None,
    ):
        self.s = s
        self.dispatcher = dispatcher
        self.access = access

    def list(self):
        statement = select(Recommendation).join(Member).where(Recommendation.deleted_at.is_(None))
        if self.access is not None:
            statement = statement.where(self.access.member_scope())
        return list(self.s.scalars(statement))

    def create(self, c: RecommendationCreate):
        self._member(c.member_id)
        x = Recommendation(**c.model_dump(), status="draft")
        self.s.add(x)
        self.s.commit()
        self.s.refresh(x)
        return x

    def get(self, id: UUID):
        x = self.s.scalar(
            select(Recommendation).where(
                Recommendation.id == id, Recommendation.deleted_at.is_(None)
            )
        )
        if x is None:
            raise ApiError(
                status_code=404, code="NOT_FOUND", message="推薦プロジェクトが見つかりません。"
            )
        self._member(x.member_id)
        return x

    def update(self, id: UUID, c: RecommendationUpdate):
        x = self.get(id)
        for k, v in c.model_dump(exclude_unset=True).items():
            setattr(x, k, v)
        self.s.commit()
        self.s.refresh(x)
        return x

    def delete(self, id: UUID):
        x = self.get(id)
        x.deleted_at = datetime.now(UTC)
        self.s.commit()

    def list_versions(self, recommendation_id: UUID) -> Sequence[RecommendationVersion]:
        self.get(recommendation_id)
        return list(
            self.s.scalars(
                select(RecommendationVersion)
                .where(
                    RecommendationVersion.recommendation_id == recommendation_id,
                    RecommendationVersion.deleted_at.is_(None),
                )
                .order_by(RecommendationVersion.version_no.desc())
            )
        )

    def get_version(self, version_id: UUID) -> RecommendationVersion:
        version = self.s.scalar(
            select(RecommendationVersion).where(
                RecommendationVersion.id == version_id,
                RecommendationVersion.deleted_at.is_(None),
            )
        )
        if version is None:
            raise ApiError(
                status_code=404,
                code="NOT_FOUND",
                message="推薦文バージョンが見つかりません。",
            )
        return version

    def update_version(
        self, version_id: UUID, command: RecommendationVersionUpdate
    ) -> RecommendationVersion:
        source = self.get_version(version_id)
        version = RecommendationVersion(
            recommendation_id=source.recommendation_id,
            version_no=self._next_version_no(source.recommendation_id),
            version_type="manager_edited",
            content=command.content,
        )
        self.s.add(version)
        self.s.flush()
        for evidence in self.version_evidences(source.id):
            self.s.add(
                RecommendationEvidence(
                    recommendation_version_id=version.id,
                    paragraph_no=evidence.paragraph_no,
                    source_type=evidence.source_type,
                    source_id=evidence.source_id,
                    evidence_text=evidence.evidence_text,
                )
            )
        self.s.commit()
        self.s.refresh(version)
        return version

    def request_generation(self, recommendation_id: UUID) -> AiJob:
        self.get(recommendation_id)
        job = AiJob(
            job_type="recommendation_generation",
            target_type="recommendation",
            target_id=recommendation_id,
            status="queued",
            retry_count=0,
        )
        self.s.add(job)
        self.s.commit()
        self.s.refresh(job)
        if self.dispatcher is not None:
            self.dispatcher.enqueue_recommendation_generation(job.id)
        return job

    def finalize(self, recommendation_id: UUID, command: RecommendationFinalize) -> Recommendation:
        recommendation = self.get(recommendation_id)
        version = self.get_version(command.version_id)
        if version.recommendation_id != recommendation.id:
            raise ApiError(
                status_code=422,
                code="INVALID_VERSION",
                message="確定対象の版はこの推薦プロジェクトに属していません。",
            )
        recommendation.status = "manager_confirmed"
        recommendation.finalized_at = datetime.now(UTC)
        self.s.commit()
        self.s.refresh(recommendation)
        return recommendation

    def _next_version_no(self, recommendation_id: UUID) -> int:
        current = self.s.scalar(
            select(func.max(RecommendationVersion.version_no)).where(
                RecommendationVersion.recommendation_id == recommendation_id
            )
        )
        return (current or 0) + 1

    def version_evidences(self, version_id: UUID) -> Sequence[RecommendationEvidence]:
        self.get_version(version_id)
        return list(
            self.s.scalars(
                select(RecommendationEvidence)
                .where(
                    RecommendationEvidence.recommendation_version_id == version_id,
                    RecommendationEvidence.deleted_at.is_(None),
                )
                .order_by(RecommendationEvidence.paragraph_no, RecommendationEvidence.created_at)
            )
        )

    def _member(self, member_id: UUID) -> Member:
        if self.access is not None:
            return self.access.ensure_member(member_id)
        member = self.s.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if member is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="メンバーが見つかりません。")
        return member
