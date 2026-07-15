from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


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


class AiSettingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str | None = None
    base_url: AnyHttpUrl | None = None
    model: str | None = None
    api_key_secret_ref: str | None = None
    timeout_seconds: int | None = Field(default=None, ge=1, le=600)
    max_retries: int | None = Field(default=None, ge=0, le=10)
    prompt_version: str | None = None


class AiSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    provider: str
    base_url: str
    model: str
    api_key_secret_ref: str
    timeout_seconds: int
    max_retries: int
    prompt_version: str
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime
