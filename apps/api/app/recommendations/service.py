from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import (
    Member,
    Recommendation,
    RecommendationEvidence,
    RecommendationVersion,
)
from app.recommendations.schemas import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationVersionUpdate,
)


class RecommendationService:
    def __init__(self, s: Session):
        self.s = s

    def list(self):
        return list(
            self.s.scalars(select(Recommendation).where(Recommendation.deleted_at.is_(None)))
        )

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
        version = self.get_version(version_id)
        version.content = command.content
        version.version_type = "manager_edited"
        self.s.commit()
        self.s.refresh(version)
        return version

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
        member = self.s.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if member is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="メンバーが見つかりません。")
        return member
