from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecommendationCreate(BaseModel):
    member_id: UUID
    purpose: str = Field(min_length=1, max_length=255)
    target_name: str | None = None
    target_requirements: str | None = None
    emphasis_points: str | None = None
    tone: str | None = None
    output_format: str | None = None


class RecommendationUpdate(BaseModel):
    purpose: str | None = Field(default=None, min_length=1, max_length=255)
    target_name: str | None = None
    target_requirements: str | None = None
    emphasis_points: str | None = None
    tone: str | None = None
    output_format: str | None = None


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    purpose: str
    target_name: str | None
    target_requirements: str | None
    emphasis_points: str | None
    tone: str | None
    output_format: str | None
    status: str
    finalized_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class RecommendationVersionUpdate(BaseModel):
    content: str = Field(min_length=1)


class RecommendationVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation_id: UUID
    version_no: int
    version_type: str
    content: str
    created_by: UUID | None
    created_at: datetime
    deleted_at: datetime | None


class RecommendationEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recommendation_version_id: UUID
    paragraph_no: int
    source_type: str
    source_id: UUID
    evidence_text: str
    created_at: datetime
    deleted_at: datetime | None
