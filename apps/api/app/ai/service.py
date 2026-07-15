from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.dispatcher import AiJobDispatcher
from app.ai.schemas import AiAnalysisUpdate
from app.core.errors import ApiError
from app.infrastructure.models import AiAnalysis, AiJob, ProjectExperience


class AiService:
    def __init__(self, session: Session, dispatcher: AiJobDispatcher | None = None) -> None:
        self.session = session
        self.dispatcher = dispatcher

    def request_project_analysis(self, project_id: UUID) -> AiJob:
        project = self.session.scalar(
            select(ProjectExperience).where(
                ProjectExperience.id == project_id,
                ProjectExperience.deleted_at.is_(None),
            )
        )
        if project is None:
            raise ApiError(
                status_code=404,
                code="NOT_FOUND",
                message="案件経験が見つかりません。",
                details={"project_id": str(project_id)},
            )
        job = AiJob(
            job_type="project_analysis",
            target_type="project_experience",
            target_id=project_id,
            status="queued",
            requested_by=None,
            retry_count=0,
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        if self.dispatcher is not None:
            self.dispatcher.enqueue_project_analysis(job.id)
        return job

    def get_job(self, job_id: UUID) -> AiJob:
        job = self.session.get(AiJob, job_id)
        if job is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="AIジョブが見つかりません。")
        return job

    def get_analysis(self, analysis_id: UUID) -> AiAnalysis:
        analysis = self.session.scalar(
            select(AiAnalysis).where(
                AiAnalysis.id == analysis_id,
                AiAnalysis.deleted_at.is_(None),
            )
        )
        if analysis is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="AI分析が見つかりません。")
        return analysis

    def update_analysis(self, analysis_id: UUID, command: AiAnalysisUpdate) -> AiAnalysis:
        analysis = self.get_analysis(analysis_id)
        for name, value in command.model_dump(exclude_unset=True).items():
            setattr(analysis, name, value)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis
