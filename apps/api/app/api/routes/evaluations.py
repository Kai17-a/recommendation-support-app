from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.evaluations.schemas import EvaluationCreate, EvaluationResponse, EvaluationUpdate
from app.evaluations.service import EvaluationService
from app.infrastructure.database import get_session
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(tags=["evaluations"])


def service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> EvaluationService:
    return EvaluationService(session, AccessControl(session, user))


@router.get("/api/v1/members/{member_id}/evaluations", response_model=list[EvaluationResponse])
async def list_evaluations(
    member_id: UUID, app_service: EvaluationService = Depends(service)
) -> list[EvaluationResponse]:
    return [EvaluationResponse.model_validate(x) for x in app_service.list_for_member(member_id)]


@router.post(
    "/api/v1/members/{member_id}/evaluations",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation(
    member_id: UUID, command: EvaluationCreate, app_service: EvaluationService = Depends(service)
) -> EvaluationResponse:
    return EvaluationResponse.model_validate(app_service.create(member_id, command))


@router.patch("/api/v1/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: UUID,
    command: EvaluationUpdate,
    app_service: EvaluationService = Depends(service),
) -> EvaluationResponse:
    return EvaluationResponse.model_validate(app_service.update(evaluation_id, command))


@router.delete("/api/v1/evaluations/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: UUID, app_service: EvaluationService = Depends(service)
) -> Response:
    app_service.delete(evaluation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
