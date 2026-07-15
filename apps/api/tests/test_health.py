import httpx
import pytest

from app.api.routes import health
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_health_check_returns_ok() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


@pytest.mark.anyio
async def test_readiness_reports_dependencies(monkeypatch) -> None:
    monkeypatch.setattr(
        health,
        "dependency_status",
        lambda: {"database": True, "redis": True, "object_storage": False},
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


@pytest.mark.anyio
async def test_request_size_limit() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health", headers={"content-length": "999999999"})
    assert response.status_code == 413
