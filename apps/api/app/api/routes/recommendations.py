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

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])
version_router = APIRouter(prefix="/api/v1/recommendation-versions", tags=["recommendations"])


def svc(s: Session = Depends(get_session)):
    return RecommendationService(s, DramatiqAiJobDispatcher())


@router.get("", response_model=list[RecommendationResponse])
def list_(x: RecommendationService = Depends(svc)):
    return x.list()


@router.post("", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def create(c: RecommendationCreate, x: RecommendationService = Depends(svc)):
    return x.create(c)


@router.get("/{id}", response_model=RecommendationResponse)
def get(id: UUID, x: RecommendationService = Depends(svc)):
    return x.get(id)


@router.patch("/{id}", response_model=RecommendationResponse)
def update(id: UUID, c: RecommendationUpdate, x: RecommendationService = Depends(svc)):
    return x.update(id, c)


@router.delete("/{id}", status_code=204)
def delete(id: UUID, x: RecommendationService = Depends(svc)):
    x.delete(id)
    return Response(status_code=204)


@router.post("/{id}/generate", response_model=AiJobResponse, status_code=status.HTTP_202_ACCEPTED)
def generate(id: UUID, x: RecommendationService = Depends(svc)):
    return x.request_generation(id)


@router.post("/{id}/finalize", response_model=RecommendationResponse)
def finalize(id: UUID, command: RecommendationFinalize, x: RecommendationService = Depends(svc)):
    return x.finalize(id, command)


@router.get("/{id}/versions", response_model=list[RecommendationVersionResponse])
def list_versions(id: UUID, x: RecommendationService = Depends(svc)):
    return x.list_versions(id)


@version_router.get("/{version_id}", response_model=RecommendationVersionResponse)
def get_version(version_id: UUID, x: RecommendationService = Depends(svc)):
    return x.get_version(version_id)


@version_router.patch("/{version_id}", response_model=RecommendationVersionResponse)
def update_version(
    version_id: UUID,
    command: RecommendationVersionUpdate,
    x: RecommendationService = Depends(svc),
):
    return x.update_version(version_id, command)


@version_router.get("/{version_id}/evidences", response_model=list[RecommendationEvidenceResponse])
def list_version_evidences(version_id: UUID, x: RecommendationService = Depends(svc)):
    return x.version_evidences(version_id)
