from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.skills.schemas import EvidenceResponse, MemberSkillResponse, SkillCreate, SkillUpdate
from app.skills.service import SkillService

router = APIRouter(tags=["skills"])


def service(s: Session = Depends(get_session)) -> SkillService:
    return SkillService(s)


@router.get("/api/v1/members/{member_id}/skills", response_model=list[MemberSkillResponse])
def list_skills(member_id: UUID, x: SkillService = Depends(service)) -> list[MemberSkillResponse]:
    return [MemberSkillResponse.model_validate(v) for v in x.list_for_member(member_id)]


@router.post(
    "/api/v1/members/{member_id}/skills",
    response_model=MemberSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    member_id: UUID, c: SkillCreate, x: SkillService = Depends(service)
) -> MemberSkillResponse:
    return MemberSkillResponse.model_validate(x.create(member_id, c))


@router.patch("/api/v1/member-skills/{id}", response_model=MemberSkillResponse)
def update_skill(
    id: UUID, c: SkillUpdate, x: SkillService = Depends(service)
) -> MemberSkillResponse:
    return MemberSkillResponse.model_validate(x.update(id, c))


@router.delete("/api/v1/member-skills/{id}", status_code=204)
def delete_skill(id: UUID, x: SkillService = Depends(service)) -> Response:
    x.delete(id)
    return Response(status_code=204)


@router.get("/api/v1/member-skills/{id}/evidences", response_model=list[EvidenceResponse])
def evidences(id: UUID, x: SkillService = Depends(service)) -> list[EvidenceResponse]:
    return [EvidenceResponse.model_validate(v) for v in x.evidences(id)]
