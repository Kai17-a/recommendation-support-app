import os
import time
from collections.abc import Iterator
from typing import cast
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.infrastructure.models import Department, Member, User, UserRole, UserStatus

pytestmark = pytest.mark.integration

API_URL = os.getenv("INTEGRATION_API_URL", "http://api:8000")
MOCK_URL = os.getenv("INTEGRATION_MOCK_URL", "http://mock-services:8080")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://app:change-me-for-local-development@postgres:5432/recommendation_support",
)


@pytest.fixture(scope="module")
def identities() -> Iterator[dict[str, str]]:
    engine = create_engine(DATABASE_URL)
    suffix = uuid4().hex[:8]
    with Session(engine) as session:
        department = Department(name="Integration Department", code=f"int-{suffix}")
        foreign_department = Department(name="Foreign Department", code=f"foreign-{suffix}")
        session.add_all([department, foreign_department])
        session.flush()
        operator = session.scalar(select(User).where(User.oidc_subject == "integration-operator"))
        assert operator is not None
        manager = User(
            department_id=department.id,
            name="Integration Manager",
            email=f"manager-{suffix}@example.test",
            oidc_subject=f"manager-{suffix}",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
        foreign_manager = User(
            department_id=foreign_department.id,
            name="Foreign Manager",
            email=f"foreign-{suffix}@example.test",
            oidc_subject=f"foreign-{suffix}",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
        session.add_all([manager, foreign_manager])
        session.flush()
        foreign_member = Member(
            department_id=foreign_department.id,
            manager_user_id=foreign_manager.id,
            name="Foreign Member",
            status="active",
        )
        session.add(foreign_member)
        session.commit()
        yield {
            "department_id": str(department.id),
            "manager_id": str(manager.id),
            "manager_subject": cast(str, manager.oidc_subject),
            "operator_subject": "integration-operator",
            "foreign_member_id": str(foreign_member.id),
        }
    engine.dispose()


def _headers(subject: str) -> dict[str, str]:
    response = httpx.post(f"{MOCK_URL}/token", params={"subject": subject}, timeout=10)
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _wait_for_job(client: httpx.Client, job_id: str, expected: str = "completed") -> dict:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        response = client.get(f"/api/v1/ai-jobs/{job_id}")
        response.raise_for_status()
        job = response.json()
        if job["status"] in {"completed", "failed"}:
            assert job["status"] == expected, job
            return job
        time.sleep(0.25)
    raise AssertionError(f"AI job did not finish: {job_id}")


def test_oidc_markdown_analysis_and_recommendation_workflows(identities: dict[str, str]) -> None:
    manager_headers = _headers(identities["manager_subject"])
    operator_headers = _headers(identities["operator_subject"])
    with httpx.Client(base_url=API_URL, headers=manager_headers, timeout=15) as manager:
        assert (
            manager.get("/api/v1/members", headers={"Authorization": "Bearer broken"}).status_code
            == 401
        )
        assert manager.get(f"/api/v1/members/{identities['foreign_member_id']}").status_code == 403

        member_response = manager.post(
            "/api/v1/members",
            json={
                "department_id": identities["department_id"],
                "manager_user_id": identities["manager_id"],
                "name": "Integration Member",
                "status": "active",
            },
        )
        member_response.raise_for_status()
        member_id = member_response.json()["id"]

        project_response = manager.post(
            f"/api/v1/members/{member_id}/projects",
            json={"project_name": "Integration Project", "status": "active"},
        )
        project_response.raise_for_status()
        project_id = project_response.json()["id"]

        with httpx.Client(base_url=API_URL, headers=operator_headers, timeout=15) as operator:
            setting = operator.patch(
                "/api/v1/admin/ai-settings",
                json={
                    "provider": "custom",
                    "base_url": f"{MOCK_URL}/v1",
                    "model": "integration-model",
                    "api_key_secret_ref": "E2E_AI_GATEWAY_API_KEY",
                    "timeout_seconds": 5,
                    "max_retries": 1,
                    "prompt_version": "integration-v1",
                },
            )
            setting.raise_for_status()

        markdown = """# 案件報告
## メンバー名
Integration Member
## 案件名
Integration Project
## 報告種別
定期報告
## 対象期間
2026-01-01 - 2026-01-31
## 実施内容
API結合試験を実施
## 成果
主要フローを検証
## 使用技術
Python, PostgreSQL
"""
        imported = manager.post(
            f"/api/v1/projects/{project_id}/markdown-imports",
            data={"member_id": member_id, "retain_file": "false"},
            files={"file": ("report.md", markdown, "text/markdown")},
        )
        imported.raise_for_status()
        _wait_for_job(manager, imported.json()["job_id"])
        import_detail = manager.get(
            f"/api/v1/markdown-imports/{imported.json()['import_id']}"
        ).json()
        assert import_detail["status"] in {"completed", "completed_with_warnings"}
        assert import_detail["project_report_id"] is not None

        analysis_job = manager.post(f"/api/v1/projects/{project_id}/analyses")
        analysis_job.raise_for_status()
        _wait_for_job(manager, analysis_job.json()["id"])

        recommendation = manager.post(
            "/api/v1/recommendations",
            json={"member_id": member_id, "purpose": "結合試験用推薦文"},
        )
        recommendation.raise_for_status()
        recommendation_id = recommendation.json()["id"]
        generation_job = manager.post(f"/api/v1/recommendations/{recommendation_id}/generate")
        generation_job.raise_for_status()
        _wait_for_job(manager, generation_job.json()["id"])
        versions = manager.get(f"/api/v1/recommendations/{recommendation_id}/versions")
        versions.raise_for_status()
        assert versions.json()[0]["version_type"] == "ai_generated"
        finalized = manager.post(
            f"/api/v1/recommendations/{recommendation_id}/finalize",
            json={"version_id": versions.json()[0]["id"]},
        )
        finalized.raise_for_status()
        assert finalized.json()["status"] == "manager_confirmed"


def test_ai_gateway_failure_marks_job_failed(identities: dict[str, str]) -> None:
    manager_headers = _headers(identities["manager_subject"])
    operator_headers = _headers(identities["operator_subject"])
    with httpx.Client(base_url=API_URL, headers=manager_headers, timeout=15) as manager:
        members = manager.get("/api/v1/members")
        members.raise_for_status()
        member_id = members.json()[0]["id"]
        project = manager.post(
            f"/api/v1/members/{member_id}/projects",
            json={"project_name": "Failure Project", "status": "active"},
        )
        project.raise_for_status()
        with httpx.Client(base_url=API_URL, headers=operator_headers, timeout=15) as operator:
            response = operator.patch(
                "/api/v1/admin/ai-settings", json={"model": "failure-model", "max_retries": 0}
            )
            response.raise_for_status()
        job = manager.post(f"/api/v1/projects/{project.json()['id']}/analyses")
        job.raise_for_status()
        failed = _wait_for_job(manager, job.json()["id"], expected="failed")
        assert failed["error_message"]
