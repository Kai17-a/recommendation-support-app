import redis
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.core.config import settings
from app.infrastructure.database import engine
from app.markdown_imports.storage import S3MarkdownObjectStorage, get_markdown_object_storage

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """APIプロセスがリクエストを受け付けられることを確認する。"""
    return {"status": "ok"}


def dependency_status() -> dict[str, bool]:
    checks = {"database": False, "redis": False, "object_storage": False}
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass
    try:
        client = redis.Redis.from_url(settings.redis_url, socket_timeout=2)
        checks["redis"] = bool(client.ping())
    except Exception:
        pass
    try:
        storage = get_markdown_object_storage()
        if isinstance(storage, S3MarkdownObjectStorage):
            storage.client.head_bucket(Bucket=storage.bucket)
            checks["object_storage"] = True
    except Exception:
        pass
    return checks


@router.get("/ready")
async def readiness_check(response: Response) -> dict[str, object]:
    checks = dependency_status()
    ready = all(checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if ready else "not_ready", "checks": checks}
