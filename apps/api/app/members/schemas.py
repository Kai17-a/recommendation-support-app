from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.models import MemberStatus


class MemberCreate(BaseModel):
    department_id: UUID
    manager_user_id: UUID
    name: str = Field(min_length=1, max_length=255)
    status: MemberStatus = MemberStatus.ACTIVE


class MemberUpdate(BaseModel):
    department_id: UUID | None = None
    manager_user_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    status: MemberStatus | None = None


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    department_id: UUID
    manager_user_id: UUID
    name: str
    status: MemberStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
