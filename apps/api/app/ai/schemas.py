from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AiJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_type: str
    target_type: str
    target_id: UUID
    status: str
    requested_by: UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    retry_count: int
    created_at: datetime


class AiAnalysisUpdate(BaseModel):
    analysis_result: dict[str, Any] | None = None
    evidence_map: dict[str, Any] | None = None


class AiAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ai_job_id: UUID
    target_type: str
    target_id: UUID
    provider: str
    model: str
    prompt_version: str
    analysis_result: dict[str, Any]
    evidence_map: dict[str, Any]
    source_snapshot: str
    executed_at: datetime
    updated_at: datetime
