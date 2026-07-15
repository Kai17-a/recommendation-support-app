from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectCreate(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    customer_name: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)
    period_from: date | None = None
    period_to: date | None = None
    status: str = Field(min_length=1, max_length=100)
    overview: str | None = None

    @model_validator(mode="after")
    def validate_period(self) -> ProjectCreate:
        has_invalid_period = (
            self.period_from is not None
            and self.period_to is not None
            and self.period_to < self.period_from
        )
        if has_invalid_period:
            raise ValueError("終了日は開始日以降にしてください。")
        return self


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, min_length=1, max_length=255)
    customer_name: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=255)
    period_from: date | None = None
    period_to: date | None = None
    status: str | None = Field(default=None, min_length=1, max_length=100)
    overview: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    member_id: UUID
    project_name: str
    customer_name: str | None
    industry: str | None
    period_from: date | None
    period_to: date | None
    status: str
    overview: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
