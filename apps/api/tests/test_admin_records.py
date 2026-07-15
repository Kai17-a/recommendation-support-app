from collections.abc import Generator
from datetime import UTC, datetime

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.admin.service import AdminService
from app.api.routes.admin import get_admin_service
from app.infrastructure.models import (
    Base,
    Department,
    Member,
    MemberStatus,
    ProjectExperience,
    ProjectReport,
    RetentionPolicy,
    User,
    UserRole,
    UserStatus,
)
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def deleted_records() -> Generator[dict[str, str]]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    with factory() as session:
        department = Department(name="開発部", code="DEV-AUDIT")
        session.add(department)
        session.flush()
        manager = User(
            department_id=department.id,
            name="管理者",
            email="audit-manager@example.com",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
        session.add(manager)
        session.flush()
        member = Member(
            department_id=department.id,
            manager_user_id=manager.id,
            name="削除済みメンバー",
            status=MemberStatus.INACTIVE,
            deleted_at=datetime(2020, 1, 1, tzinfo=UTC),
        )
        session.add(member)
        session.flush()
        project = ProjectExperience(
            member_id=member.id,
            project_name="監査テスト",
            status="completed",
        )
        session.add(project)
        session.flush()
        report = ProjectReport(
            project_experience_id=project.id,
            report_type="periodic",
            report_date=datetime(2020, 1, 1, tzinfo=UTC).date(),
            deleted_at=datetime(2020, 1, 1, tzinfo=UTC),
        )
        session.add(report)
        session.add(
            RetentionPolicy(
                target_type="project_report",
                retention_months=12,
                purge_enabled=True,
                require_manual_approval=True,
            )
        )
        session.commit()
        ids = {"member": str(member.id), "report": str(report.id)}

    def override() -> Generator[AdminService]:
        with factory() as session:
            yield AdminService(session)

    app.dependency_overrides[get_admin_service] = override
    try:
        yield ids
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_deleted_record_restore_and_audit_log(deleted_records: dict[str, str]) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        listed = await client.get("/api/v1/admin/deleted-records?target_type=member")
        assert listed.status_code == 200
        assert listed.json()[0]["target_id"] == deleted_records["member"]

        restored = await client.post(
            f"/api/v1/admin/deleted-records/member/{deleted_records['member']}/restore"
        )
        assert restored.status_code == 200
        assert restored.json()["action"] == "restore"

        assert (await client.get("/api/v1/admin/deleted-records?target_type=member")).json() == []
        audits = await client.get(
            f"/api/v1/admin/audit-logs?target_type=member&target_id={deleted_records['member']}"
        )
        assert audits.status_code == 200
        assert audits.json()[0]["action"] == "restore"


@pytest.mark.anyio
async def test_purge_requires_approval_and_keeps_summary_only(
    deleted_records: dict[str, str],
) -> None:
    url = f"/api/v1/admin/deleted-records/project_report/{deleted_records['report']}/purge"
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        denied = await client.post(url, json={"manual_approval": False})
        assert denied.status_code == 409
        assert denied.json()["error"]["code"] == "PURGE_NOT_ALLOWED"

        purged = await client.post(url, json={"manual_approval": True, "reason": "保持期限経過"})
        assert purged.status_code == 200
        assert purged.json()["action"] == "purge"
        assert purged.json()["before_data"]["summary"] == {
            "id": deleted_records["report"],
            "target_type": "project_report",
            "deleted_at": "2020-01-01T00:00:00",
        }
        assert "work_detail" not in str(purged.json()["before_data"])
        assert (
            await client.get("/api/v1/admin/deleted-records?target_type=project_report")
        ).json() == []


@pytest.mark.anyio
async def test_deleted_records_reject_unknown_target_type(
    deleted_records: dict[str, str],
) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/deleted-records?target_type=unknown")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
