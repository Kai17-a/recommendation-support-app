from collections.abc import Generator
from uuid import UUID

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.projects import get_project_service
from app.api.routes.reports import get_report_service
from app.infrastructure.models import (
    Base,
    Department,
    Member,
    MemberStatus,
    User,
    UserRole,
    UserStatus,
)
from app.main import app
from app.projects.service import ProjectService
from app.reports.service import ReportService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def member_id() -> Generator[str]:
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
        session.flush()
        member = Member(
            department_id=department.id,
            manager_user_id=manager.id,
            name="佐藤 花子",
            status=MemberStatus.ACTIVE,
        )
        session.add(member)
        session.commit()
        created_member_id = str(member.id)

    def override_service() -> Generator[ProjectService]:
        with session_factory() as session:
            yield ProjectService(session)

    def override_report_service() -> Generator[ReportService]:
        with session_factory() as session:
            yield ReportService(session)

    app.dependency_overrides[get_project_service] = override_service
    app.dependency_overrides[get_report_service] = override_report_service
    try:
        yield created_member_id
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_project_lifecycle(member_id: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            f"/api/v1/members/{member_id}/projects",
            json={
                "project_name": "推薦基盤構築",
                "customer_name": "社内人事部",
                "industry": "情報サービス",
                "period_from": "2026-04-01",
                "status": "in_progress",
                "overview": "推薦業務支援システムの基盤を構築した。",
            },
        )
        assert created.status_code == 201
        project_id = UUID(created.json()["id"])

        listed = await client.get(f"/api/v1/members/{member_id}/projects")
        assert listed.status_code == 200
        assert [project["id"] for project in listed.json()] == [str(project_id)]

        updated = await client.patch(
            f"/api/v1/projects/{project_id}",
            json={"period_to": "2026-06-30", "status": "completed"},
        )
        assert updated.status_code == 200
        assert updated.json()["status"] == "completed"

        deleted = await client.delete(f"/api/v1/projects/{project_id}")
        assert deleted.status_code == 204

        hidden = await client.get(f"/api/v1/projects/{project_id}")
        assert hidden.status_code == 404
        assert hidden.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.anyio
async def test_project_creation_rejects_unknown_member(member_id: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/members/00000000-0000-0000-0000-000000000001/projects",
            json={"project_name": "推薦基盤構築", "status": "in_progress"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.anyio
async def test_project_report_lifecycle(member_id: str) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        project = await client.post(
            f"/api/v1/members/{member_id}/projects",
            json={"project_name": "推薦基盤構築", "status": "in_progress"},
        )
        project_id = project.json()["id"]
        created = await client.post(
            f"/api/v1/projects/{project_id}/reports",
            json={
                "report_type": "periodic",
                "report_date": "2026-04-30",
                "achievements": "API基盤を実装した。",
            },
        )
        assert created.status_code == 201
        report_id = created.json()["id"]
        updated = await client.patch(
            f"/api/v1/reports/{report_id}", json={"manager_comment": "確認済み"}
        )
        assert updated.status_code == 200
        assert updated.json()["manager_comment"] == "確認済み"
        assert (await client.delete(f"/api/v1/reports/{report_id}")).status_code == 204
        assert (await client.get(f"/api/v1/reports/{report_id}")).status_code == 404
