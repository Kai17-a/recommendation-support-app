from calendar import monthrange
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.admin.audit import record_audit
from app.admin.schemas import AiSettingUpdate, PurgeRequest, RetentionPolicyUpdate
from app.core.errors import ApiError
from app.infrastructure.models import (
    AiAnalysis,
    AiSetting,
    AuditLog,
    Member,
    MemberEvaluation,
    MemberSkill,
    MemberSkillEvidence,
    ProjectExperience,
    ProjectReport,
    Recommendation,
    RecommendationEvidence,
    RecommendationVersion,
    RetentionPolicy,
)

DELETABLE_MODELS = {
    "member": Member,
    "project_experience": ProjectExperience,
    "project_report": ProjectReport,
    "member_evaluation": MemberEvaluation,
    "member_skill": MemberSkill,
    "member_skill_evidence": MemberSkillEvidence,
    "recommendation": Recommendation,
    "recommendation_version": RecommendationVersion,
    "recommendation_evidence": RecommendationEvidence,
    "ai_analysis": AiAnalysis,
}


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
        if changes.get("base_url") is not None:
            changes["base_url"] = str(changes["base_url"]).rstrip("/")
        before = None
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
            self.session.flush()
        else:
            before = {name: getattr(setting, name) for name in changes}
        for name, value in changes.items():
            setattr(setting, name, value)
        record_audit(
            self.session,
            target_type="ai_setting",
            target_id=setting.id,
            action="settings_change",
            before_data=before,
            after_data={name: getattr(setting, name) for name in changes},
            changed_fields={
                name: {
                    "before": before.get(name) if before else None,
                    "after": getattr(setting, name),
                }
                for name in changes
            },
        )
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
        changes = command.model_dump(exclude_unset=True)
        before = {name: getattr(policy, name) for name in changes}
        for name, value in changes.items():
            setattr(policy, name, value)
        record_audit(
            self.session,
            target_type="retention_policy",
            target_id=policy.id,
            action="settings_change",
            before_data=before,
            after_data={name: getattr(policy, name) for name in changes},
            changed_fields={
                name: {"before": before[name], "after": getattr(policy, name)} for name in changes
            },
        )
        self.session.commit()
        self.session.refresh(policy)
        return policy

    def list_audit_logs(
        self, target_type: str | None = None, target_id: UUID | None = None
    ) -> Sequence[AuditLog]:
        statement: Select[tuple[AuditLog]] = select(AuditLog)
        if target_type is not None:
            statement = statement.where(AuditLog.target_type == target_type)
        if target_id is not None:
            statement = statement.where(AuditLog.target_id == target_id)
        return list(self.session.scalars(statement.order_by(AuditLog.changed_at.desc())))

    def list_deleted_records(self, target_type: str | None = None) -> list[dict[str, object]]:
        models = self._selected_models(target_type)
        records: list[dict[str, object]] = []
        for name, model in models:
            rows = self.session.scalars(
                select(model).where(model.deleted_at.is_not(None)).order_by(model.deleted_at.desc())
            )
            records.extend(
                {"target_type": name, "target_id": row.id, "deleted_at": row.deleted_at}
                for row in rows
            )
        return sorted(records, key=lambda item: item["deleted_at"], reverse=True)  # type: ignore[arg-type]

    def restore_deleted_record(self, target_type: str, target_id: UUID) -> AuditLog:
        record = self._deleted_record(target_type, target_id)
        deleted_at = record.deleted_at
        record.deleted_at = None
        audit = record_audit(
            self.session,
            target_type=target_type,
            target_id=target_id,
            action="restore",
            before_data={"summary": {"id": str(target_id), "deleted_at": deleted_at.isoformat()}},
            after_data={"summary": {"id": str(target_id), "deleted_at": None}},
            changed_fields={"deleted_at": {"before": deleted_at.isoformat(), "after": None}},
        )
        self.session.commit()
        self.session.refresh(audit)
        return audit

    def purge_deleted_record(
        self, target_type: str, target_id: UUID, command: PurgeRequest
    ) -> AuditLog:
        if not command.manual_approval:
            self._purge_not_allowed("物理削除には手動承認が必要です。")
        record = self._deleted_record(target_type, target_id)
        policy = self.session.scalar(
            select(RetentionPolicy).where(RetentionPolicy.target_type == target_type)
        )
        if policy is None or not policy.purge_enabled:
            self._purge_not_allowed("対象種別の物理削除は許可されていません。")
        assert policy is not None
        eligible_at = _add_months(record.deleted_at, policy.retention_months)
        now = datetime.now(UTC)
        if eligible_at.tzinfo is None:
            eligible_at = eligible_at.replace(tzinfo=UTC)
        if eligible_at > now:
            self._purge_not_allowed("保持期限を経過していません。")

        audit = record_audit(
            self.session,
            target_type=target_type,
            target_id=target_id,
            action="purge",
            before_data={
                "summary": {
                    "id": str(target_id),
                    "target_type": target_type,
                    "deleted_at": record.deleted_at.isoformat(),
                }
            },
            after_data=None,
            changed_fields=None,
            reason=command.reason,
        )
        self.session.delete(record)
        self.session.commit()
        self.session.refresh(audit)
        return audit

    def _selected_models(self, target_type: str | None):
        if target_type is None:
            return DELETABLE_MODELS.items()
        model = DELETABLE_MODELS.get(target_type)
        if model is None:
            raise ApiError(
                status_code=422,
                code="VALIDATION_ERROR",
                message="削除対象種別が不正です。",
                details={"target_type": target_type},
            )
        return ((target_type, model),)

    def _deleted_record(self, target_type: str, target_id: UUID):
        selected = self._selected_models(target_type)
        _, model = next(iter(selected))
        record = self.session.scalar(
            select(model).where(model.id == target_id, model.deleted_at.is_not(None))
        )
        if record is None:
            raise ApiError(
                status_code=404, code="NOT_FOUND", message="削除済みレコードが見つかりません。"
            )
        return record

    @staticmethod
    def _purge_not_allowed(message: str) -> None:
        raise ApiError(status_code=409, code="PURGE_NOT_ALLOWED", message=message)


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)
