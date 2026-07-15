import json
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any
from uuid import UUID

import httpx
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.ai.gateway import (
    AiGatewayOutputInvalid,
    AiGatewayTimeout,
    OpenAiCompatibleGateway,
)
from app.ai.orchestrator import ProjectAnalysisOrchestrator, RecommendationGenerationOrchestrator
from app.infrastructure.models import (
    AiJob,
    AiSetting,
    Base,
    ProjectExperience,
    ProjectReport,
    Recommendation,
    RecommendationEvidence,
)


class StaticSecretResolver:
    def resolve(self, reference: str) -> str:
        assert reference == "ai-gateway-key"
        return "resolved-secret"


def test_openai_compatible_gateway_sends_secret_and_decodes_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer resolved-secret"
        payload = json.loads(request.content)
        assert payload["model"] == "analysis-default"
        assert payload["response_format"] == {"type": "json_object"}
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"fact_summary": []}'}}]},
        )

    gateway = OpenAiCompatibleGateway(
        StaticSecretResolver(), transport=httpx.MockTransport(handler)
    )
    result = gateway.complete_json(
        base_url="https://gateway.example.com/v1",
        api_key_secret_ref="ai-gateway-key",
        model="analysis-default",
        messages=[{"role": "user", "content": "data"}],
        timeout_seconds=30,
    )
    assert result == {"fact_summary": []}


def test_openai_compatible_gateway_maps_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    gateway = OpenAiCompatibleGateway(
        StaticSecretResolver(), transport=httpx.MockTransport(handler)
    )
    with pytest.raises(AiGatewayTimeout):
        gateway.complete_json(
            base_url="https://gateway.example.com/v1",
            api_key_secret_ref="ai-gateway-key",
            model="analysis-default",
            messages=[],
            timeout_seconds=1,
        )


class FakeGateway:
    def __init__(self, output: dict[str, Any]) -> None:
        self.output = output
        self.calls = 0

    def complete_json(
        self,
        *,
        base_url: str,
        api_key_secret_ref: str,
        model: str,
        messages: Sequence[Mapping[str, str]],
        timeout_seconds: int,
    ) -> dict[str, Any]:
        self.calls += 1
        assert "ランキング、スコアリングは行わず" in messages[0]["content"]
        assert "<data>" in messages[1]["content"]
        return self.output


def test_project_analysis_orchestrator_saves_metadata_snapshot_and_evidence() -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = ProjectExperience(
            member_id=UUID("00000000-0000-0000-0000-000000000001"),
            project_name="推薦基盤構築",
            status="completed",
        )
        session.add(project)
        session.flush()
        report = ProjectReport(
            project_experience_id=project.id,
            report_type="final",
            report_date=date(2026, 7, 15),
            achievements="APIを実装した。",
        )
        session.add(report)
        session.add(
            AiSetting(
                provider="custom",
                base_url="https://gateway.example.com/v1",
                model="analysis-default",
                api_key_secret_ref="ai-gateway-key",
                timeout_seconds=30,
                max_retries=2,
                prompt_version="project-analysis-v1",
            )
        )
        session.flush()
        job = AiJob(
            job_type="project_analysis",
            target_type="project_experience",
            target_id=project.id,
            status="running",
            retry_count=0,
        )
        session.add(job)
        session.flush()

        gateway = FakeGateway(
            {
                "fact_summary": ["APIを実装した。"],
                "skill_candidates": ["FastAPI"],
                "strength_candidates": [],
                "evidence": [
                    {
                        "source_type": "project_report",
                        "source_id": str(report.id),
                        "quote_or_summary": "APIを実装した。",
                    }
                ],
                "missing_information": [],
            }
        )
        analysis = ProjectAnalysisOrchestrator(session, gateway).execute(job)

        assert analysis.model == "analysis-default"
        assert analysis.prompt_version == "project-analysis-v1"
        assert analysis.analysis_result["fact_summary"] == ["APIを実装した。"]
        assert analysis.evidence_map["evidence"]
        assert str(report.id) in analysis.source_snapshot

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_project_analysis_orchestrator_rejects_unknown_evidence() -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = ProjectExperience(
            member_id=UUID("00000000-0000-0000-0000-000000000001"),
            project_name="推薦基盤構築",
            status="completed",
        )
        session.add_all(
            [
                project,
                AiSetting(
                    provider="custom",
                    base_url="https://gateway.example.com/v1",
                    model="analysis-default",
                    api_key_secret_ref="ai-gateway-key",
                    timeout_seconds=30,
                    max_retries=0,
                    prompt_version="project-analysis-v1",
                ),
            ]
        )
        session.flush()
        job = AiJob(
            job_type="project_analysis",
            target_type="project_experience",
            target_id=project.id,
            status="running",
            retry_count=0,
        )
        session.add(job)
        session.flush()
        gateway = FakeGateway(
            {
                "fact_summary": ["根拠のない事実"],
                "skill_candidates": [],
                "strength_candidates": [],
                "evidence": [
                    {
                        "source_type": "project_report",
                        "source_id": "00000000-0000-0000-0000-000000000099",
                        "quote_or_summary": "存在しない根拠",
                    }
                ],
                "missing_information": [],
            }
        )
        with pytest.raises(AiGatewayOutputInvalid):
            ProjectAnalysisOrchestrator(session, gateway).execute(job)

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_recommendation_orchestrator_saves_version_evidence_and_metadata() -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = ProjectExperience(
            member_id=UUID("00000000-0000-0000-0000-000000000001"),
            project_name="推薦基盤構築",
            status="completed",
        )
        recommendation = Recommendation(
            member_id=project.member_id,
            purpose="顧客案件への推薦",
            status="draft",
        )
        session.add_all([project, recommendation])
        session.flush()
        session.add_all(
            [
                ProjectReport(
                    project_experience_id=project.id,
                    report_type="final",
                    report_date=date(2026, 7, 15),
                    achievements="APIを実装した。",
                ),
                AiSetting(
                    provider="custom",
                    base_url="https://gateway.example.com/v1",
                    model="recommendation-default",
                    api_key_secret_ref="ai-gateway-key",
                    timeout_seconds=30,
                    max_retries=0,
                    prompt_version="recommendation-v1",
                ),
            ]
        )
        # The FK is intentionally not enforced by this SQLite unit database.
        from app.infrastructure.models import Member

        member = Member(
            id=project.member_id,
            department_id=UUID("00000000-0000-0000-0000-000000000002"),
            manager_user_id=UUID("00000000-0000-0000-0000-000000000003"),
            name="佐藤 花子",
            status="active",
        )
        session.add(member)
        session.flush()
        report = session.scalar(select(ProjectReport))
        assert report is not None
        job = AiJob(
            job_type="recommendation_generation",
            target_type="recommendation",
            target_id=recommendation.id,
            status="running",
            retry_count=0,
        )
        session.add(job)
        session.flush()
        gateway = FakeGateway(
            {
                "draft": [
                    {
                        "paragraph_no": 1,
                        "text": "API実装経験があります。",
                        "evidence": [
                            {
                                "source_type": "project_report",
                                "source_id": str(report.id),
                                "quote_or_summary": "APIを実装した。",
                            }
                        ],
                    }
                ],
                "warnings": ["推薦先の詳細が不足しています。"],
            }
        )
        analysis, version = RecommendationGenerationOrchestrator(session, gateway).execute(job)
        assert analysis.model == "recommendation-default"
        assert analysis.prompt_version == "recommendation-v1"
        assert analysis.analysis_result["warnings"]
        assert version.version_no == 1
        assert version.content == "API実装経験があります。"
        evidence = session.scalar(select(RecommendationEvidence))
        assert evidence is not None
        assert evidence.source_id == report.id

    Base.metadata.drop_all(engine)
    engine.dispose()
