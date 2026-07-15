from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.dispatcher import ProjectAnalysisDispatcher
from app.ai.schemas import AiAnalysisUpdate
from app.core.errors import ApiError
from app.infrastructure.models import (
    AiAnalysis,
    AiJob,
    MarkdownImport,
    ProjectExperience,
    Recommendation,
)
from app.security.authorization import AccessControl


class AiService:
    def __init__(
        self,
        session: Session,
        dispatcher: ProjectAnalysisDispatcher | None = None,
        access: AccessControl | None = None,
    ) -> None:
        self.session = session
        self.dispatcher = dispatcher
        self.access = access

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
        if self.access is not None:
            self.access.ensure_member(project.member_id)
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
        self._authorize_target(job.target_type, job.target_id)
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
        self._authorize_target(analysis.target_type, analysis.target_id)
        return analysis

    def _authorize_target(self, target_type: str, target_id: UUID) -> None:
        if self.access is None:
            return
        if target_type == "project_experience":
            project = self.session.get(ProjectExperience, target_id)
            if project is None:
                raise ApiError(status_code=404, code="NOT_FOUND", message="対象が見つかりません。")
            self.access.ensure_member(project.member_id)
            return
        if target_type == "recommendation":
            recommendation = self.session.get(Recommendation, target_id)
            if recommendation is not None:
                self.access.ensure_member(recommendation.member_id)
                return
        if target_type == "markdown_import":
            imported = self.session.get(MarkdownImport, target_id)
            if imported is not None:
                self.access.ensure_member(imported.member_id)
                return
        raise ApiError(status_code=403, code="FORBIDDEN", message="このAIジョブを参照できません。")

    def update_analysis(self, analysis_id: UUID, command: AiAnalysisUpdate) -> AiAnalysis:
        analysis = self.get_analysis(analysis_id)
        for name, value in command.model_dump(exclude_unset=True).items():
            setattr(analysis, name, value)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis
