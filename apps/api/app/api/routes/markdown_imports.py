from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.ai.dispatcher import DramatiqAiJobDispatcher
from app.infrastructure.database import get_session
from app.markdown_imports.schemas import (
    MarkdownImportResponse,
    MarkdownWarningResponse,
    MarkdownWarningUpdate,
)
from app.markdown_imports.service import MarkdownImportService
from app.markdown_imports.storage import get_markdown_object_storage
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(tags=["markdown-imports"])


def get_markdown_import_service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> MarkdownImportService:
    return MarkdownImportService(
        session,
        DramatiqAiJobDispatcher(),
        get_markdown_object_storage(),
        AccessControl(session, user),
    )


@router.post(
    "/api/v1/projects/{project_id}/markdown-imports",
    response_model=MarkdownImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_markdown_import(
    project_id: UUID,
    member_id: UUID = Form(),
    file: UploadFile = File(),
    retain_file: bool = Form(False),
    service: MarkdownImportService = Depends(get_markdown_import_service),
) -> MarkdownImportResponse:
    return service.create(project_id, member_id, file.filename, await file.read(), retain_file)


@router.get("/api/v1/markdown-imports/{import_id}", response_model=MarkdownImportResponse)
async def get_markdown_import(
    import_id: UUID, service: MarkdownImportService = Depends(get_markdown_import_service)
) -> MarkdownImportResponse:
    return service.get(import_id)


@router.get(
    "/api/v1/markdown-imports/{import_id}/warnings", response_model=list[MarkdownWarningResponse]
)
async def list_markdown_import_warnings(
    import_id: UUID, service: MarkdownImportService = Depends(get_markdown_import_service)
) -> list[MarkdownWarningResponse]:
    return [MarkdownWarningResponse.model_validate(row) for row in service.warnings(import_id)]


@router.patch(
    "/api/v1/markdown-import-warnings/{warning_id}", response_model=MarkdownWarningResponse
)
async def update_markdown_import_warning(
    warning_id: UUID,
    command: MarkdownWarningUpdate,
    service: MarkdownImportService = Depends(get_markdown_import_service),
) -> MarkdownWarningResponse:
    return MarkdownWarningResponse.model_validate(service.update_warning(warning_id, command))
