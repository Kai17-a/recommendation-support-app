from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReportFields(BaseModel):
    report_type: str = Field(min_length=1, max_length=100)
    period_from: date | None = None
    period_to: date | None = None
    report_date: date
    work_detail: str | None = None
    achievements: str | None = None
    technologies: str | None = None
    difficulties: str | None = None
    improvements: str | None = None
    member_comment: str | None = None
    manager_comment: str | None = None


class ReportCreate(ReportFields):
    pass


class ReportUpdate(BaseModel):
    report_type: str | None = Field(default=None, min_length=1, max_length=100)
    period_from: date | None = None
    period_to: date | None = None
    report_date: date | None = None
    work_detail: str | None = None
    achievements: str | None = None
    technologies: str | None = None
    difficulties: str | None = None
    improvements: str | None = None
    member_comment: str | None = None
    manager_comment: str | None = None


class ReportResponse(ReportFields):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_experience_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
