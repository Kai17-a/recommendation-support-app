from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.reports.schemas import ReportCreate, ReportResponse, ReportUpdate
from app.reports.service import ReportService
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(tags=["reports"])


def get_report_service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> ReportService:
    return ReportService(session, AccessControl(session, user))


@router.get("/api/v1/projects/{project_id}/reports", response_model=list[ReportResponse])
async def list_reports(
    project_id: UUID, service: ReportService = Depends(get_report_service)
) -> list[ReportResponse]:
    return [ReportResponse.model_validate(r) for r in service.list_for_project(project_id)]


@router.post(
    "/api/v1/projects/{project_id}/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    project_id: UUID, command: ReportCreate, service: ReportService = Depends(get_report_service)
) -> ReportResponse:
    return ReportResponse.model_validate(service.create(project_id, command))


@router.get("/api/v1/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID, service: ReportService = Depends(get_report_service)
) -> ReportResponse:
    return ReportResponse.model_validate(service.get(report_id))


@router.patch("/api/v1/reports/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID, command: ReportUpdate, service: ReportService = Depends(get_report_service)
) -> ReportResponse:
    return ReportResponse.model_validate(service.update(report_id, command))


@router.delete("/api/v1/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID, service: ReportService = Depends(get_report_service)
) -> Response:
    service.delete(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
