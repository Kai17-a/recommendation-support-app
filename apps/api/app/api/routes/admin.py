from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.admin.schemas import (
    AiSettingResponse,
    AiSettingUpdate,
    RetentionPolicyResponse,
    RetentionPolicyUpdate,
)
from app.admin.service import AdminService
from app.infrastructure.database import get_session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def get_admin_service(session: Session = Depends(get_session)) -> AdminService:
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
