from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = None
    description: str | None = None
    source_type: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1, max_length=100)
    manager_comment: str | None = None


class SkillUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=100)
    manager_comment: str | None = None


class MemberSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    skill_id: UUID
    source_type: str
    status: str
    manager_comment: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_skill_id: UUID
    source_type: str
    source_id: UUID
    evidence_text: str
    created_at: datetime
