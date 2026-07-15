from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RetentionPolicyUpdate(BaseModel):
    retention_months: int | None = Field(default=None, ge=1)
    purge_enabled: bool | None = None
    require_manual_approval: bool | None = None


class RetentionPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    target_type: str
    retention_months: int
    purge_enabled: bool
    require_manual_approval: bool
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime
