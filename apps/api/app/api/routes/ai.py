from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.ai.dispatcher import DramatiqAiJobDispatcher
from app.ai.schemas import AiAnalysisResponse, AiAnalysisUpdate, AiJobResponse
from app.ai.service import AiService
from app.infrastructure.database import get_session
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(tags=["ai"])


def get_ai_service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> AiService:
    return AiService(session, DramatiqAiJobDispatcher(), AccessControl(session, user))


@router.post(
    "/api/v1/projects/{project_id}/analyses",
    response_model=AiJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_project_analysis(
    project_id: UUID,
    service: AiService = Depends(get_ai_service),
) -> AiJobResponse:
    return AiJobResponse.model_validate(service.request_project_analysis(project_id))


@router.get("/api/v1/ai-jobs/{job_id}", response_model=AiJobResponse)
async def get_ai_job(job_id: UUID, service: AiService = Depends(get_ai_service)) -> AiJobResponse:
    return AiJobResponse.model_validate(service.get_job(job_id))


@router.get("/api/v1/ai-analyses/{analysis_id}", response_model=AiAnalysisResponse)
async def get_ai_analysis(
    analysis_id: UUID, service: AiService = Depends(get_ai_service)
) -> AiAnalysisResponse:
    return AiAnalysisResponse.model_validate(service.get_analysis(analysis_id))


@router.patch("/api/v1/ai-analyses/{analysis_id}", response_model=AiAnalysisResponse)
async def update_ai_analysis(
    analysis_id: UUID,
    command: AiAnalysisUpdate,
    service: AiService = Depends(get_ai_service),
) -> AiAnalysisResponse:
    return AiAnalysisResponse.model_validate(service.update_analysis(analysis_id, command))
