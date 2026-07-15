from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """APIプロセスがリクエストを受け付けられることを確認する。"""
    return {"status": "ok"}
