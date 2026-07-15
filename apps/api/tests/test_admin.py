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

    def override_service() -> Generator[AdminService]:
        with session_factory() as session:
            yield AdminService(session)

    app.dependency_overrides[get_admin_service] = override_service
    try:
        yield policy_id
    finally:
        app.dependency_overrides.clear()
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
