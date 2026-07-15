from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.schemas import RetentionPolicyUpdate
from app.core.errors import ApiError
from app.infrastructure.models import RetentionPolicy


class AdminService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_retention_policies(self) -> Sequence[RetentionPolicy]:
        statement = select(RetentionPolicy).order_by(RetentionPolicy.target_type)
        return list(self.session.scalars(statement))

    def update_retention_policy(
        self, policy_id: UUID, command: RetentionPolicyUpdate
    ) -> RetentionPolicy:
        policy = self.session.get(RetentionPolicy, policy_id)
        if policy is None:
            raise ApiError(
                status_code=404,
                code="NOT_FOUND",
                message="保持ポリシーが見つかりません。",
            )
        for name, value in command.model_dump(exclude_unset=True).items():
            setattr(policy, name, value)
        self.session.commit()
        self.session.refresh(policy)
        return policy
