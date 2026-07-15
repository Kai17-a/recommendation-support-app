from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.admin.schemas import (
    AiSettingResponse,
    AiSettingUpdate,
    AuditLogResponse,
    DeletedRecordResponse,
    PurgeRequest,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)
from app.admin.service import AdminService
from app.infrastructure.database import get_session
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def get_admin_service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> AdminService:
    AccessControl(session, user).require_system_operator()
    return AdminService(session)


@router.get("/ai-settings", response_model=AiSettingResponse)
def get_ai_setting(service: AdminService = Depends(get_admin_service)) -> AiSettingResponse:
    return AiSettingResponse.model_validate(service.get_ai_setting())


@router.patch("/ai-settings", response_model=AiSettingResponse)
def update_ai_setting(
    command: AiSettingUpdate,
    service: AdminService = Depends(get_admin_service),
) -> AiSettingResponse:
    return AiSettingResponse.model_validate(service.update_ai_setting(command))


@router.get("/retention-policies", response_model=list[RetentionPolicyResponse])
def list_retention_policies(
    service: AdminService = Depends(get_admin_service),
) -> Sequence[RetentionPolicyResponse]:
    return [
        RetentionPolicyResponse.model_validate(policy)
        for policy in service.list_retention_policies()
    ]


@router.patch("/retention-policies/{policy_id}", response_model=RetentionPolicyResponse)
def update_retention_policy(
    policy_id: UUID,
    command: RetentionPolicyUpdate,
    service: AdminService = Depends(get_admin_service),
) -> RetentionPolicyResponse:
    policy = service.update_retention_policy(policy_id, command)
    return RetentionPolicyResponse.model_validate(policy)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(
    target_type: str | None = None,
    target_id: UUID | None = None,
    service: AdminService = Depends(get_admin_service),
) -> Sequence[AuditLogResponse]:
    return [
        AuditLogResponse.model_validate(log)
        for log in service.list_audit_logs(target_type, target_id)
    ]


@router.get("/deleted-records", response_model=list[DeletedRecordResponse])
def list_deleted_records(
    target_type: str | None = None,
    service: AdminService = Depends(get_admin_service),
) -> Sequence[DeletedRecordResponse]:
    return [
        DeletedRecordResponse.model_validate(item)
        for item in service.list_deleted_records(target_type)
    ]


@router.post("/deleted-records/{target_type}/{target_id}/restore", response_model=AuditLogResponse)
def restore_deleted_record(
    target_type: str,
    target_id: UUID,
    service: AdminService = Depends(get_admin_service),
) -> AuditLogResponse:
    return AuditLogResponse.model_validate(service.restore_deleted_record(target_type, target_id))


@router.post("/deleted-records/{target_type}/{target_id}/purge", response_model=AuditLogResponse)
def purge_deleted_record(
    target_type: str,
    target_id: UUID,
    command: PurgeRequest,
    service: AdminService = Depends(get_admin_service),
) -> AuditLogResponse:
    return AuditLogResponse.model_validate(
        service.purge_deleted_record(target_type, target_id, command)
    )
