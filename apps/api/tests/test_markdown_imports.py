from collections.abc import Generator
from uuid import UUID

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.markdown_imports import get_markdown_import_service
from app.infrastructure.models import (
    Base,
    Department,
    MarkdownImportWarning,
    Member,
    MemberStatus,
    ProjectExperience,
    User,
    UserRole,
    UserStatus,
)
from app.main import app
from app.markdown_imports.parser import parse_markdown
from app.markdown_imports.service import MarkdownImportService


class MemoryStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> None:
        self.objects[key] = data

    def get(self, key: str) -> bytes:
        return self.objects[key]

    def delete(self, key: str) -> None:
        self.objects.pop(key, None)


class RecordingDispatcher:
    def __init__(self) -> None:
        self.jobs: list[UUID] = []

    def enqueue_project_analysis(self, job_id: UUID) -> None:
        pass

    def enqueue_markdown_import(self, job_id: UUID) -> None:
        self.jobs.append(job_id)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def context() -> Generator[
    tuple[sessionmaker[Session], UUID, UUID, RecordingDispatcher, MemoryStorage]
]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    dispatcher = RecordingDispatcher()
    storage = MemoryStorage()
    with factory() as session:
        department = Department(name="開発", code="dev")
        session.add(department)
        session.flush()
        user = User(
            department_id=department.id,
            name="上司",
            email="boss@example.com",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
        session.flush()
        member = Member(
            department_id=department.id,
            manager_user_id=user.id,
            name="山田 太郎",
            status=MemberStatus.ACTIVE,
        )
        session.add(member)
        session.flush()
        project = ProjectExperience(member_id=member.id, project_name="基幹刷新", status="active")
        session.add(project)
        session.commit()
        member_id, project_id = member.id, project.id

    def override() -> Generator[MarkdownImportService]:
        with factory() as session:
            yield MarkdownImportService(session, dispatcher, storage)

    app.dependency_overrides[get_markdown_import_service] = override
    yield factory, member_id, project_id, dispatcher, storage
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_markdown_import_lifecycle(context) -> None:
    factory, member_id, project_id, dispatcher, storage = context
    content = """# 案件報告
## メンバー名
山田 太郎
## 案件名
基幹刷新
## 報告種別
定期報告
## 対象期間
2026-07-01 ～ 2026-07-15
## 実施内容
- API実装
## 成果
- リリース
## 使用技術
- Python, PostgreSQL
"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/projects/{project_id}/markdown-imports",
            data={"member_id": str(member_id), "retain_file": "false"},
            files={"file": ("report.md", content.encode(), "text/markdown")},
        )
        assert response.status_code == 202
        body = response.json()
        assert body["status"] == "queued"
        assert len(dispatcher.jobs) == 1
        assert list(storage.objects.values()) == [content.encode()]

        fetched = await client.get(f"/api/v1/markdown-imports/{body['import_id']}")
        assert fetched.status_code == 200
        assert fetched.json()["job_id"] == body["job_id"]

        with factory() as session:
            warning = MarkdownImportWarning(
                markdown_import_id=UUID(body["import_id"]),
                warning_code="TEST",
                message="確認してください。",
                resolution_status="unresolved",
            )
            session.add(warning)
            session.commit()
            warning_id = warning.id
        warnings = await client.get(f"/api/v1/markdown-imports/{body['import_id']}/warnings")
        assert warnings.status_code == 200
        assert len(warnings.json()) == 1
        resolved = await client.patch(
            f"/api/v1/markdown-import-warnings/{warning_id}",
            json={"resolution_status": "resolved"},
        )
        assert resolved.status_code == 200
        assert resolved.json()["resolved_at"] is not None


@pytest.mark.anyio
async def test_rejects_invalid_and_duplicate_files(context) -> None:
    _, member_id, project_id, _, _ = context
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        invalid = await client.post(
            f"/api/v1/projects/{project_id}/markdown-imports",
            data={"member_id": str(member_id)},
            files={"file": ("report.txt", b"text", "text/plain")},
        )
        assert invalid.status_code == 422
        first = await client.post(
            f"/api/v1/projects/{project_id}/markdown-imports",
            data={"member_id": str(member_id)},
            files={"file": ("report.md", b"# report", "text/markdown")},
        )
        assert first.status_code == 202
        duplicate = await client.post(
            f"/api/v1/projects/{project_id}/markdown-imports",
            data={"member_id": str(member_id)},
            files={"file": ("again.md", b"# report", "text/markdown")},
        )
        assert duplicate.status_code == 409


def test_deterministic_parser_extracts_template_fields() -> None:
    parsed = parse_markdown(
        """## 報告種別
終了報告
## 対象期間
2026-06-01 ～ 2026-06-30
## 実施内容
- 実装
## 使用技術
- Python
"""
    )
    assert parsed.report_type == "final"
    assert parsed.period_from is not None
    assert parsed.period_to is not None
    assert parsed.period_from.isoformat() == "2026-06-01"
    assert parsed.period_to.isoformat() == "2026-06-30"
    assert parsed.work_detail == "実装"
    assert parsed.technologies == "Python"
