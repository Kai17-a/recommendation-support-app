from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.recommendations.schemas import (
    RecommendationCreate,
    RecommendationResponse,
    RecommendationUpdate,
)
from app.recommendations.service import RecommendationService

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


def svc(s: Session = Depends(get_session)):
    return RecommendationService(s)


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
