from collections.abc import AsyncGenerator, Generator
from uuid import UUID

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.recommendations import svc as get_recommendation_service
from app.infrastructure.models import (
    Base,
    Department,
    Member,
    MemberStatus,
    RecommendationEvidence,
    RecommendationVersion,
    User,
    UserRole,
    UserStatus,
)
from app.main import app
from app.recommendations.service import RecommendationService


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def recommendation_test_database() -> Generator[tuple[str, sessionmaker[Session]]]:
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
        member_id = str(member.id)

    async def override_service() -> AsyncGenerator[RecommendationService]:
        with session_factory() as session:
            yield RecommendationService(session)

    app.dependency_overrides[get_recommendation_service] = override_service
    try:
        yield member_id, session_factory
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.mark.anyio
async def test_recommendation_version_and_evidence_lifecycle(
    recommendation_test_database: tuple[str, sessionmaker[Session]],
) -> None:
    member_id, session_factory = recommendation_test_database
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/recommendations",
            json={"member_id": member_id, "purpose": "顧客案件への推薦"},
        )
        assert created.status_code == 201
        recommendation_id = UUID(created.json()["id"])

        with session_factory() as session:
            version = RecommendationVersion(
                recommendation_id=recommendation_id,
                version_no=1,
                version_type="ai_generated",
                content="案件経験に基づく推薦文です。",
            )
            session.add(version)
            session.flush()
            evidence = RecommendationEvidence(
                recommendation_version_id=version.id,
                paragraph_no=1,
                source_type="project_report",
                source_id=UUID(member_id),
                evidence_text="案件でAPI基盤を実装した。",
            )
            session.add(evidence)
            session.commit()
            version_id = str(version.id)

        versions = await client.get(f"/api/v1/recommendations/{recommendation_id}/versions")
        assert versions.status_code == 200
        assert versions.json()[0]["version_no"] == 1

        evidence_response = await client.get(
            f"/api/v1/recommendation-versions/{version_id}/evidences"
        )
        assert evidence_response.status_code == 200
        assert evidence_response.json()[0]["evidence_text"] == "案件でAPI基盤を実装した。"

        updated = await client.patch(
            f"/api/v1/recommendation-versions/{version_id}",
            json={"content": "上司が確認して編集した推薦文です。"},
        )
        assert updated.status_code == 200
        assert updated.json()["version_type"] == "manager_edited"
        assert updated.json()["content"] == "上司が確認して編集した推薦文です。"
        assert updated.json()["id"] != version_id
        assert updated.json()["version_no"] == 2

        original = await client.get(f"/api/v1/recommendation-versions/{version_id}")
        assert original.json()["content"] == "案件経験に基づく推薦文です。"
        copied_evidence = await client.get(
            f"/api/v1/recommendation-versions/{updated.json()['id']}/evidences"
        )
        assert len(copied_evidence.json()) == 1

        generated = await client.post(f"/api/v1/recommendations/{recommendation_id}/generate")
        assert generated.status_code == 202
        assert generated.json()["job_type"] == "recommendation_generation"
        assert generated.json()["status"] == "queued"

        missing_version = await client.post(
            f"/api/v1/recommendations/{recommendation_id}/finalize", json={}
        )
        assert missing_version.status_code == 422

        finalized = await client.post(
            f"/api/v1/recommendations/{recommendation_id}/finalize",
            json={"version_id": updated.json()["id"]},
        )
        assert finalized.status_code == 200
        assert finalized.json()["status"] == "manager_confirmed"
        assert finalized.json()["finalized_at"] is not None


@pytest.mark.anyio
async def test_recommendation_creation_rejects_deleted_member(
    recommendation_test_database: tuple[str, sessionmaker[Session]],
) -> None:
    member_id, session_factory = recommendation_test_database
    with session_factory() as session:
        member = session.get(Member, UUID(member_id))
        assert member is not None
        member.deleted_at = member.created_at
        session.commit()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/recommendations",
            json={"member_id": member_id, "purpose": "顧客案件への推薦"},
        )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
