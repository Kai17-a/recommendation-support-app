from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import ProjectExperience, ProjectReport
from app.reports.schemas import ReportCreate, ReportUpdate
from app.security.authorization import AccessControl


class ReportService:
    def __init__(self, session: Session, access: AccessControl | None = None) -> None:
        self.session = session
        self.access = access

    def list_for_project(self, project_id: UUID) -> list[ProjectReport]:
        self._project(project_id)
        return list(
            self.session.scalars(
                select(ProjectReport)
                .where(
                    ProjectReport.project_experience_id == project_id,
                    ProjectReport.deleted_at.is_(None),
                )
                .order_by(ProjectReport.report_date.desc())
            )
        )

    def create(self, project_id: UUID, command: ReportCreate) -> ProjectReport:
        self._project(project_id)
        report = ProjectReport(project_experience_id=project_id, **command.model_dump())
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    def get(self, report_id: UUID) -> ProjectReport:
        report = self.session.scalar(
            select(ProjectReport).where(
                ProjectReport.id == report_id, ProjectReport.deleted_at.is_(None)
            )
        )
        if report is None:
            raise self._not_found(report_id)
        self._project(report.project_experience_id)
        return report

    def update(self, report_id: UUID, command: ReportUpdate) -> ProjectReport:
        report = self.get(report_id)
        for name, value in command.model_dump(exclude_unset=True).items():
            setattr(report, name, value)
        self.session.commit()
        self.session.refresh(report)
        return report

    def delete(self, report_id: UUID) -> None:
        report = self.get(report_id)
        report.deleted_at = datetime.now(UTC)
        self.session.commit()

    def _project(self, project_id: UUID) -> ProjectExperience:
        project = self.session.scalar(
            select(ProjectExperience).where(
                ProjectExperience.id == project_id, ProjectExperience.deleted_at.is_(None)
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
        return project

    @staticmethod
    def _not_found(report_id: UUID) -> ApiError:
        return ApiError(
            status_code=404,
            code="NOT_FOUND",
            message="案件報告が見つかりません。",
            details={"report_id": str(report_id)},
        )
