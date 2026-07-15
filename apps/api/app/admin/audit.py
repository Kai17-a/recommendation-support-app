import json
from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.infrastructure.models import AiSetting, AuditLog, Base, RetentionPolicy


def record_audit(
    session: Session,
    *,
    target_type: str,
    target_id: UUID,
    action: str,
    before_data: dict[str, object] | None = None,
    after_data: dict[str, object] | None = None,
    changed_fields: dict[str, object] | None = None,
    changed_by: UUID | None = None,
    request_id: UUID | None = None,
    reason: str | None = None,
) -> AuditLog:
    """監査ログを現在のトランザクションへ追加する（commitは呼び出し側の責務）。"""
    audit = AuditLog(
        target_type=target_type,
        target_id=target_id,
        action=action,
        before_data=before_data,
        after_data=after_data,
        changed_fields=changed_fields,
        changed_by=changed_by,
        request_id=request_id,
        reason=reason,
    )
    session.add(audit)
    return audit


def _json_value(value: object) -> object:
    if isinstance(value, UUID | datetime | date | Enum):
        return str(value)
    return value


@event.listens_for(Session, "before_flush")
def create_automatic_audit_logs(
    session: Session, _flush_context: object, _instances: object
) -> None:
    """主要データの作成・更新・論理削除を同一トランザクションで記録する。"""
    if session.info.get("creating_audit_logs"):
        return
    session.info["creating_audit_logs"] = True
    try:
        candidates = [*session.new, *session.dirty]
        for target in candidates:
            if (
                not isinstance(target, Base)
                or isinstance(target, AuditLog | AiSetting | RetentionPolicy)
                or target in session.deleted
                or not hasattr(target, "id")
            ):
                continue
            state = inspect(target)
            changes: dict[str, object] = {}
            before: dict[str, object] = {}
            after: dict[str, object] = {}
            for attribute in state.mapper.column_attrs:
                history = state.attrs[attribute.key].history
                if target in session.new or history.has_changes():
                    old = history.deleted[0] if history.deleted else None
                    new = getattr(target, attribute.key)
                    before[attribute.key] = _json_value(old)
                    after[attribute.key] = _json_value(new)
                    changes[attribute.key] = {"before": _json_value(old), "after": _json_value(new)}
            if not changes:
                continue
            if target.id is None:
                target.id = uuid4()
                after["id"] = str(target.id)
            action = "create" if target in session.new else "update"
            if "deleted_at" in changes:
                if before.get("deleted_at") is None and after.get("deleted_at") is not None:
                    action = "delete"
                elif before.get("deleted_at") is not None and after.get("deleted_at") is None:
                    action = "restore"
            record_audit(
                session,
                target_type=target.__tablename__.removesuffix("s"),
                target_id=target.id,
                action=action,
                before_data=json.loads(json.dumps(before, default=str)),
                after_data=json.loads(json.dumps(after, default=str)),
                changed_fields=json.loads(json.dumps(changes, default=str)),
            )
    finally:
        session.info["creating_audit_logs"] = False
