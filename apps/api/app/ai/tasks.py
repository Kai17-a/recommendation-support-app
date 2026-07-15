from datetime import UTC, datetime
from uuid import UUID

import dramatiq

from app.ai.broker import broker as broker
from app.ai.gateway import EnvironmentSecretResolver, OpenAiCompatibleGateway
from app.ai.orchestrator import ProjectAnalysisOrchestrator, RecommendationGenerationOrchestrator
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import AiJob


@dramatiq.actor(max_retries=0, queue_name="ai")
def run_project_analysis(job_id: str) -> None:
    with SessionLocal() as session:
        job = session.get(AiJob, UUID(job_id))
        if job is None or job.status == "completed":
            return
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.error_message = None
        session.commit()

        try:
            gateway = OpenAiCompatibleGateway(EnvironmentSecretResolver())
            ProjectAnalysisOrchestrator(session, gateway).execute(job)
            job.status = "completed"
            job.completed_at = datetime.now(UTC)
            session.commit()
        except Exception as error:
            retry_count = job.retry_count
            session.rollback()
            job = session.get(AiJob, UUID(job_id))
            if job is not None:
                job.status = "failed"
                job.completed_at = datetime.now(UTC)
                job.error_message = str(error)[:4000]
                job.retry_count = retry_count
                session.commit()
            raise


@dramatiq.actor(max_retries=0, queue_name="ai")
def run_recommendation_generation(job_id: str) -> None:
    with SessionLocal() as session:
        job = session.get(AiJob, UUID(job_id))
        if job is None or job.status == "completed":
            return
        job.status = "running"
        job.started_at = datetime.now(UTC)
        job.error_message = None
        session.commit()
        try:
            gateway = OpenAiCompatibleGateway(EnvironmentSecretResolver())
            RecommendationGenerationOrchestrator(session, gateway).execute(job)
            job.status = "completed"
            job.completed_at = datetime.now(UTC)
            session.commit()
        except Exception as error:
            retry_count = job.retry_count
            session.rollback()
            job = session.get(AiJob, UUID(job_id))
            if job is not None:
                job.status = "failed"
                job.completed_at = datetime.now(UTC)
                job.error_message = str(error)[:4000]
                job.retry_count = retry_count
                session.commit()
            raise
