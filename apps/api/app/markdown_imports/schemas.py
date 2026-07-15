from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MarkdownImportResponse(BaseModel):
    import_id: UUID
    job_id: UUID
    status: str
    project_report_id: UUID | None
    warning_count: int
    extracted_skill_count: int


class MarkdownWarningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    markdown_import_id: UUID
    warning_code: str
    field_name: str | None
    source_text: str | None
    message: str
    resolution_status: str
    resolved_by: UUID | None
    resolved_at: datetime | None
    created_at: datetime


class MarkdownWarningUpdate(BaseModel):
    resolution_status: Literal["unresolved", "resolved", "ignored"]
