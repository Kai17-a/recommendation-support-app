from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.ai.dispatcher import DramatiqAiJobDispatcher
from app.ai.schemas import AiJobResponse
from app.infrastructure.database import get_session
from app.recommendations.schemas import (
    RecommendationCreate,
    RecommendationEvidenceResponse,
    RecommendationFinalize,
    RecommendationResponse,
    RecommendationUpdate,
    RecommendationVersionResponse,
    RecommendationVersionUpdate,
)
from app.recommendations.service import RecommendationService
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])
version_router = APIRouter(prefix="/api/v1/recommendation-versions", tags=["recommendations"])


def svc(s: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)):
    return RecommendationService(s, DramatiqAiJobDispatcher(), access=AccessControl(s, user))


@router.get("", response_model=list[RecommendationResponse])
async def list_(x: RecommendationService = Depends(svc)):
    return x.list()


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create(c: RecommendationCreate, x: RecommendationService = Depends(svc)):
    return x.create(c)


@router.get("/{id}", response_model=RecommendationResponse)
async def get(id: UUID, x: RecommendationService = Depends(svc)):
    return x.get(id)


@router.patch("/{id}", response_model=RecommendationResponse)
async def update(id: UUID, c: RecommendationUpdate, x: RecommendationService = Depends(svc)):
    return x.update(id, c)


@router.delete("/{id}", status_code=204)
async def delete(id: UUID, x: RecommendationService = Depends(svc)):
    x.delete(id)
    return Response(status_code=204)


@router.post("/{id}/generate", response_model=AiJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate(id: UUID, x: RecommendationService = Depends(svc)):
    return x.request_generation(id)


@router.post("/{id}/finalize", response_model=RecommendationResponse)
async def finalize(
    id: UUID, command: RecommendationFinalize, x: RecommendationService = Depends(svc)
):
    return x.finalize(id, command)


@router.get("/{id}/versions", response_model=list[RecommendationVersionResponse])
async def list_versions(id: UUID, x: RecommendationService = Depends(svc)):
    return x.list_versions(id)


@version_router.get("/{version_id}", response_model=RecommendationVersionResponse)
async def get_version(version_id: UUID, x: RecommendationService = Depends(svc)):
    return x.get_version(version_id)


@version_router.patch("/{version_id}", response_model=RecommendationVersionResponse)
async def update_version(
    version_id: UUID,
    command: RecommendationVersionUpdate,
    x: RecommendationService = Depends(svc),
):
    return x.update_version(version_id, command)


@version_router.get("/{version_id}/evidences", response_model=list[RecommendationEvidenceResponse])
async def list_version_evidences(version_id: UUID, x: RecommendationService = Depends(svc)):
    return x.version_evidences(version_id)
