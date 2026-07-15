from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Member, Recommendation
from app.recommendations.schemas import RecommendationCreate, RecommendationUpdate


class RecommendationService:
    def __init__(self, s: Session):
        self.s = s

    def list(self):
        return list(
            self.s.scalars(select(Recommendation).where(Recommendation.deleted_at.is_(None)))
        )

    def create(self, c: RecommendationCreate):
        if self.s.get(Member, c.member_id) is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="メンバーが見つかりません。")
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
