from collections.abc import AsyncGenerator, Generator
from uuid import UUID

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.members import get_member_service
from app.infrastructure.models import Base, Department, User, UserRole, UserStatus
from app.main import app
from app.members.service import MemberService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def member_references() -> Generator[dict[str, str]]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with session_factory() as session:
        department = Department(name="開発部", code="DEV")
        session.add(department)
        session.flush()
        manager = User(
            department_id=department.id,
            name="山田 管理者",
            email="manager@example.com",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
        session.add(manager)
        session.commit()
        references = {"department_id": str(department.id), "manager_user_id": str(manager.id)}

    async def override_service() -> AsyncGenerator[MemberService]:
        with session_factory() as session:
            yield MemberService(session)

    app.dependency_overrides[get_member_service] = override_service
    try:
        yield references
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_member_lifecycle(member_references: dict[str, str]) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/members",
            json={"name": "佐藤 花子", **member_references},
        )
        assert created.status_code == 201
        member_id = UUID(created.json()["id"])
        assert created.json()["status"] == "active"

        listed = await client.get("/api/v1/members")
        assert listed.status_code == 200
        assert [member["id"] for member in listed.json()] == [str(member_id)]

        updated = await client.patch(
            f"/api/v1/members/{member_id}",
            json={"name": "佐藤 花子（更新）", "status": "inactive"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "佐藤 花子（更新）"
        assert updated.json()["status"] == "inactive"

        deleted = await client.delete(f"/api/v1/members/{member_id}")
        assert deleted.status_code == 204

        hidden = await client.get(f"/api/v1/members/{member_id}")
        assert hidden.status_code == 404
        assert hidden.json()["error"]["code"] == "NOT_FOUND"

        restored = await client.post(f"/api/v1/members/{member_id}/restore")
        assert restored.status_code == 200
        assert restored.json()["deleted_at"] is None


@pytest.mark.anyio
async def test_member_creation_rejects_unknown_department(
    member_references: dict[str, str],
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/members",
            json={
                "name": "佐藤 花子",
                "department_id": "00000000-0000-0000-0000-000000000001",
                "manager_user_id": member_references["manager_user_id"],
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
