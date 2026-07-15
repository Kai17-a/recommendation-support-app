from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_session
from app.members.schemas import MemberCreate, MemberResponse, MemberUpdate
from app.members.service import MemberService
from app.security.authentication import CurrentUser, get_current_user
from app.security.authorization import AccessControl

router = APIRouter(prefix="/api/v1/members", tags=["members"])


def get_member_service(
    session: Session = Depends(get_session), user: CurrentUser = Depends(get_current_user)
) -> MemberService:
    return MemberService(session, AccessControl(session, user))


@router.get("", response_model=list[MemberResponse])
async def list_members(
    service: MemberService = Depends(get_member_service),
) -> list[MemberResponse]:
    return [MemberResponse.model_validate(member) for member in service.list_active()]


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    command: MemberCreate, service: MemberService = Depends(get_member_service)
) -> MemberResponse:
    return MemberResponse.model_validate(service.create(command))


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: UUID, service: MemberService = Depends(get_member_service)
) -> MemberResponse:
    return MemberResponse.model_validate(service.get_active(member_id))


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: UUID, command: MemberUpdate, service: MemberService = Depends(get_member_service)
) -> MemberResponse:
    return MemberResponse.model_validate(service.update(member_id, command))


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: UUID, service: MemberService = Depends(get_member_service)
) -> Response:
    service.delete(member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{member_id}/restore", response_model=MemberResponse)
async def restore_member(
    member_id: UUID, service: MemberService = Depends(get_member_service)
) -> MemberResponse:
    return MemberResponse.model_validate(service.restore(member_id))
