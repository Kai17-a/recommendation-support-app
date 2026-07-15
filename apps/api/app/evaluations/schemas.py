from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    evaluation_type: str = Field(min_length=1, max_length=100)
    evaluation_date: date
    project_experience_id: UUID | None = None
    period_from: date | None = None
    period_to: date | None = None
    strengths: str | None = None
    areas_for_improvement: str | None = None
    leadership: str | None = None
    communication: str | None = None
    problem_solving: str | None = None
    initiative: str | None = None
    manager_comment: str | None = None


class EvaluationUpdate(BaseModel):
    evaluation_type: str | None = Field(default=None, min_length=1, max_length=100)
    evaluation_date: date | None = None
    project_experience_id: UUID | None = None
    period_from: date | None = None
    period_to: date | None = None
    strengths: str | None = None
    areas_for_improvement: str | None = None
    leadership: str | None = None
    communication: str | None = None
    problem_solving: str | None = None
    initiative: str | None = None
    manager_comment: str | None = None


class EvaluationResponse(EvaluationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
