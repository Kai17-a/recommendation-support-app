from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.security.authentication import CurrentUser, get_current_user

router = APIRouter(prefix="/api/v1", tags=["authentication"])


class CurrentUserResponse(BaseModel):
    id: str
    department_id: str
    role: str
    name: str
    email: str


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(user: CurrentUser = Depends(get_current_user)) -> CurrentUserResponse:
    """画面が認可済みの導線を選ぶための操作者情報を返す。"""
    return CurrentUserResponse(
        id=str(user.id),
        department_id=str(user.department_id),
        role=user.role.value,
        name=user.name,
        email=user.email,
    )
