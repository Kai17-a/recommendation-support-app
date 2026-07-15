import hashlib
from datetime import UTC, datetime
from pathlib import PurePath
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai.dispatcher import AiJobDispatcher
from app.core.errors import ApiError
from app.infrastructure.models import (
    AiJob,
    MarkdownImport,
    MarkdownImportWarning,
    Member,
    MemberSkill,
    ProjectExperience,
)
from app.markdown_imports.schemas import MarkdownImportResponse, MarkdownWarningUpdate

MAX_FILE_SIZE = 10 * 1024 * 1024


class MarkdownImportService:
    def __init__(self, session: Session, dispatcher: AiJobDispatcher | None = None) -> None:
        self.session = session
        self.dispatcher = dispatcher

    def create(
        self, project_id: UUID, member_id: UUID, filename: str | None, data: bytes, retain: bool
    ) -> MarkdownImportResponse:
        project = self.session.scalar(
            select(ProjectExperience).where(
                ProjectExperience.id == project_id, ProjectExperience.deleted_at.is_(None)
            )
        )
        member = self.session.scalar(
            select(Member).where(Member.id == member_id, Member.deleted_at.is_(None))
        )
        if project is None or member is None:
            raise ApiError(
                status_code=404,
                code="NOT_FOUND",
                message="対象のメンバーまたは案件が見つかりません。",
            )
        if project.member_id != member_id:
            raise ApiError(
                status_code=422,
                code="PROJECT_MEMBER_MISMATCH",
                message="案件とメンバーが一致しません。",
            )
        name = PurePath(filename or "").name
        if not name.lower().endswith(".md"):
            raise ApiError(
                status_code=422,
                code="INVALID_FILE_TYPE",
                message="Markdownファイルのみ取り込めます。",
            )
        if not data or len(data) > MAX_FILE_SIZE or b"\x00" in data:
            raise ApiError(
                status_code=422,
                code="INVALID_FILE",
                message="ファイルが空、上限超過、またはバイナリです。",
            )
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ApiError(
                status_code=422,
                code="INVALID_ENCODING",
                message="UTF-8のMarkdownを指定してください。",
            ) from error
        digest = hashlib.sha256(data).hexdigest()
        row = MarkdownImport(
            member_id=member_id,
            project_experience_id=project_id,
            original_file_name=name,
            content_hash=digest,
            raw_content=content,
            file_storage_key=None,
            file_retained=retain,
            template_version="1",
            import_status="queued",
            imported_by=None,
        )
        self.session.add(row)
        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise ApiError(
                status_code=409,
                code="DUPLICATE_IMPORT",
                message="同一内容のMarkdownは取り込み済みです。",
            ) from error
        job = AiJob(
            job_type="markdown_import",
            target_type="markdown_import",
            target_id=row.id,
            status="queued",
            requested_by=None,
            retry_count=0,
        )
        self.session.add(job)
        self.session.commit()
        if self.dispatcher:
            self.dispatcher.enqueue_markdown_import(job.id)
        return self._response(row, job)

    def get(self, import_id: UUID) -> MarkdownImportResponse:
        row = self._import(import_id)
        job = self.session.scalar(
            select(AiJob)
            .where(AiJob.target_type == "markdown_import", AiJob.target_id == import_id)
            .order_by(AiJob.created_at.desc())
        )
        assert job is not None
        return self._response(row, job)

    def warnings(self, import_id: UUID) -> list[MarkdownImportWarning]:
        self._import(import_id)
        return list(
            self.session.scalars(
                select(MarkdownImportWarning)
                .where(MarkdownImportWarning.markdown_import_id == import_id)
                .order_by(MarkdownImportWarning.created_at)
            )
        )

    def update_warning(
        self, warning_id: UUID, command: MarkdownWarningUpdate
    ) -> MarkdownImportWarning:
        row = self.session.get(MarkdownImportWarning, warning_id)
        if row is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="警告が見つかりません。")
        row.resolution_status = command.resolution_status
        row.resolved_at = None if command.resolution_status == "unresolved" else datetime.now(UTC)
        row.resolved_by = None
        self.session.commit()
        self.session.refresh(row)
        return row

    def _import(self, id: UUID) -> MarkdownImport:
        row = self.session.scalar(
            select(MarkdownImport).where(
                MarkdownImport.id == id, MarkdownImport.deleted_at.is_(None)
            )
        )
        if row is None:
            raise ApiError(
                status_code=404, code="NOT_FOUND", message="Markdown取り込みが見つかりません。"
            )
        return row

    def _response(self, row: MarkdownImport, job: AiJob) -> MarkdownImportResponse:
        warnings = (
            self.session.scalar(
                select(func.count())
                .select_from(MarkdownImportWarning)
                .where(MarkdownImportWarning.markdown_import_id == row.id)
            )
            or 0
        )
        skills = 0
        if row.project_report_id:
            skills = (
                self.session.scalar(
                    select(func.count())
                    .select_from(MemberSkill)
                    .where(
                        MemberSkill.member_id == row.member_id,
                        MemberSkill.source_type == "markdown_import",
                    )
                )
                or 0
            )
        return MarkdownImportResponse(
            import_id=row.id,
            job_id=job.id,
            status=row.import_status,
            project_report_id=row.project_report_id,
            warning_count=warnings,
            extracted_skill_count=skills,
        )
