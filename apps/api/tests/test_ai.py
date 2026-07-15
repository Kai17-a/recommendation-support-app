from collections.abc import Generator
from datetime import UTC, datetime

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.service import AiService
from app.api.routes.ai import get_ai_service
from app.infrastructure.models import (
    AiAnalysis,
    AiJob,
    Base,
    Department,
    Member,
    MemberStatus,
    ProjectExperience,
    User,
    UserRole,
    UserStatus,
)
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def ai_records() -> Generator[dict[str, str]]:
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
        session.flush()
        project = ProjectExperience(
            member_id=member.id,
            project_name="推薦基盤構築",
            status="in_progress",
        )
        session.add(project)
        session.flush()
        completed_job = AiJob(
            job_type="project_analysis",
            target_type="project_experience",
            target_id=project.id,
            status="completed",
            retry_count=0,
            completed_at=datetime.now(UTC),
        )
        session.add(completed_job)
        session.flush()
        analysis = AiAnalysis(
            ai_job_id=completed_job.id,
            target_type="project_experience",
            target_id=project.id,
            provider="custom",
            model="analysis-default",
            prompt_version="project-analysis-v1",
            analysis_result={"fact_summary": ["API基盤を構築した。"]},
            evidence_map={
                "fact_summary": [
                    {"source_type": "project_experience", "source_id": str(project.id)}
                ]
            },
            source_snapshot='{"project_name":"推薦基盤構築"}',
            executed_at=datetime.now(UTC),
        )
        session.add(analysis)
        session.commit()
        ids = {"project_id": str(project.id), "analysis_id": str(analysis.id)}

    def override_service() -> Generator[AiService]:
        with session_factory() as session:
            yield AiService(session)

    app.dependency_overrides[get_ai_service] = override_service
    try:
        yield ids
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_project_analysis_job_is_accepted_and_retrievable(ai_records: dict[str, str]) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        accepted = await client.post(f"/api/v1/projects/{ai_records['project_id']}/analyses")
        assert accepted.status_code == 202
        assert accepted.json()["status"] == "queued"
        assert accepted.json()["job_type"] == "project_analysis"

        fetched = await client.get(f"/api/v1/ai-jobs/{accepted.json()['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["target_id"] == ai_records["project_id"]


@pytest.mark.anyio
async def test_ai_analysis_can_be_read_and_corrected(ai_records: dict[str, str]) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        fetched = await client.get(f"/api/v1/ai-analyses/{ai_records['analysis_id']}")
        assert fetched.status_code == 200
        assert fetched.json()["model"] == "analysis-default"
        assert fetched.json()["prompt_version"] == "project-analysis-v1"
        assert fetched.json()["evidence_map"]

        corrected = await client.patch(
            f"/api/v1/ai-analyses/{ai_records['analysis_id']}",
            json={"analysis_result": {"fact_summary": ["上司が内容を修正した。"]}},
        )
        assert corrected.status_code == 200
        assert corrected.json()["analysis_result"]["fact_summary"] == ["上司が内容を修正した。"]
        assert corrected.json()["evidence_map"]


@pytest.mark.anyio
async def test_project_analysis_rejects_unknown_project(ai_records: dict[str, str]) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/projects/00000000-0000-0000-0000-000000000001/analyses"
        )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
