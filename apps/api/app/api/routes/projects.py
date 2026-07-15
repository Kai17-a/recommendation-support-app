from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.projects.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.projects.service import ProjectService

router = APIRouter(tags=["projects"])


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    return ProjectService(session)


@router.get("/api/v1/members/{member_id}/projects", response_model=list[ProjectResponse])
def list_projects(
    member_id: UUID, service: ProjectService = Depends(get_project_service)
) -> list[ProjectResponse]:
    projects = service.list_for_member(member_id)
    return [ProjectResponse.model_validate(project) for project in projects]


@router.post(
    "/api/v1/members/{member_id}/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    member_id: UUID,
    command: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return ProjectResponse.model_validate(service.create(member_id, command))


@router.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID, service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    return ProjectResponse.model_validate(service.get_active(project_id))


@router.patch("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    command: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return ProjectResponse.model_validate(service.update(project_id, command))


@router.delete("/api/v1/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID, service: ProjectService = Depends(get_project_service)
) -> Response:
    service.delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
