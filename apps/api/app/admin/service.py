from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.schemas import AiSettingUpdate, RetentionPolicyUpdate
from app.core.errors import ApiError
from app.infrastructure.models import AiSetting, RetentionPolicy


class AdminService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_retention_policies(self) -> Sequence[RetentionPolicy]:
        statement = select(RetentionPolicy).order_by(RetentionPolicy.target_type)
        return list(self.session.scalars(statement))

    def get_ai_setting(self) -> AiSetting:
        setting = self.session.scalar(select(AiSetting).order_by(AiSetting.created_at).limit(1))
        if setting is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="AI設定が見つかりません。")
        return setting

    def update_ai_setting(self, command: AiSettingUpdate) -> AiSetting:
        setting = self.session.scalar(select(AiSetting).order_by(AiSetting.created_at).limit(1))
        changes = command.model_dump(exclude_unset=True)
        if setting is None:
            required = {
                "provider",
                "base_url",
                "model",
                "api_key_secret_ref",
                "timeout_seconds",
                "max_retries",
                "prompt_version",
            }
            missing = sorted(required - changes.keys())
            if missing:
                raise ApiError(
                    status_code=422,
                    code="VALIDATION_ERROR",
                    message="AI設定の初回登録には全項目が必要です。",
                    details={"missing_fields": missing},
                )
            setting = AiSetting(**changes)
            self.session.add(setting)
        for name, value in changes.items():
            if name == "base_url" and value is not None:
                value = str(value).rstrip("/")
            setattr(setting, name, value)
        self.session.commit()
        self.session.refresh(setting)
        return setting

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
