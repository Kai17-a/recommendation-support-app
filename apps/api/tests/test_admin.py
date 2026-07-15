from collections.abc import Generator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.admin.service import AdminService
from app.api.routes.admin import get_admin_service
from app.infrastructure.models import Base, RetentionPolicy
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def retention_policy_id() -> Generator[str]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with session_factory() as session:
        policy = RetentionPolicy(
            target_type="project_report",
            retention_months=60,
            purge_enabled=False,
            require_manual_approval=True,
        )
        session.add(policy)
        session.commit()
        policy_id = str(policy.id)

    service_session = session_factory()

    async def override_service() -> AdminService:
        return AdminService(service_session)

    app.dependency_overrides[get_admin_service] = override_service
    try:
        yield policy_id
    finally:
        app.dependency_overrides.clear()
        service_session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_retention_policy_lifecycle(retention_policy_id: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        listed = await client.get("/api/v1/admin/retention-policies")
        assert listed.status_code == 200
        assert listed.json()[0]["id"] == retention_policy_id
        assert listed.json()[0]["retention_months"] == 60

        updated = await client.patch(
            f"/api/v1/admin/retention-policies/{retention_policy_id}",
            json={"retention_months": 84, "purge_enabled": True},
        )
        assert updated.status_code == 200
        assert updated.json()["retention_months"] == 84
        assert updated.json()["purge_enabled"] is True
        assert updated.json()["require_manual_approval"] is True


@pytest.mark.anyio
async def test_retention_policy_update_rejects_unknown_policy(retention_policy_id: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            "/api/v1/admin/retention-policies/00000000-0000-0000-0000-000000000001",
            json={"retention_months": 84},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.anyio
async def test_ai_setting_can_be_read_and_updated_without_accepting_api_key(
    retention_policy_id: str,
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        missing = await client.get("/api/v1/admin/ai-settings")
        assert missing.status_code == 204

        created = await client.patch(
            "/api/v1/admin/ai-settings",
            json={
                "provider": "custom",
                "base_url": "https://gateway.example.com/v1/",
                "model": "analysis-default",
                "api_key_secret_ref": "ai-gateway-key",
                "timeout_seconds": 120,
                "max_retries": 2,
                "prompt_version": "project-analysis-v1",
            },
        )
        assert created.status_code == 200
        assert created.json()["base_url"] == "https://gateway.example.com/v1"
        assert created.json()["api_key_secret_ref"] == "ai-gateway-key"

        updated = await client.patch(
            "/api/v1/admin/ai-settings",
            json={"model": "analysis-v2", "timeout_seconds": 90},
        )
        assert updated.status_code == 200
        assert updated.json()["model"] == "analysis-v2"
        assert updated.json()["timeout_seconds"] == 90

        rejected = await client.patch(
            "/api/v1/admin/ai-settings",
            json={"api_key": "must-not-be-stored"},
        )
        assert rejected.status_code == 422
