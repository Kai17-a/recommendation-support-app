from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """すべての永続化モデルの基底クラス。"""


class UserRole(StrEnum):
    MANAGER = "manager"
    SYSTEM_OPERATOR = "system_operator"


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MemberStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    oidc_subject: Mapped[str | None] = mapped_column(String(255), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Member(Base):
    __tablename__ = "members"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id"), index=True)
    manager_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[MemberStatus] = mapped_column(Enum(MemberStatus, name="member_status"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    deleted_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))


class ProjectExperience(Base):
    __tablename__ = "project_experiences"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), index=True)
    project_name: Mapped[str] = mapped_column(String(255))
    customer_name: Mapped[str | None] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(255))
    period_from: Mapped[date | None] = mapped_column(Date)
    period_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(100))
    overview: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class ProjectReport(Base):
    __tablename__ = "project_reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    project_experience_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_experiences.id"), index=True
    )
    report_type: Mapped[str] = mapped_column(String(100))
    period_from: Mapped[date | None] = mapped_column(Date)
    period_to: Mapped[date | None] = mapped_column(Date)
    report_date: Mapped[date] = mapped_column(Date)
    work_detail: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[str | None] = mapped_column(Text)
    technologies: Mapped[str | None] = mapped_column(Text)
    difficulties: Mapped[str | None] = mapped_column(Text)
    improvements: Mapped[str | None] = mapped_column(Text)
    member_comment: Mapped[str | None] = mapped_column(Text)
    manager_comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class MemberEvaluation(Base):
    __tablename__ = "member_evaluations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), index=True)
    project_experience_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_experiences.id"))
    evaluation_type: Mapped[str] = mapped_column(String(100))
    period_from: Mapped[date | None] = mapped_column(Date)
    period_to: Mapped[date | None] = mapped_column(Date)
    evaluation_date: Mapped[date] = mapped_column(Date)
    strengths: Mapped[str | None] = mapped_column(Text)
    areas_for_improvement: Mapped[str | None] = mapped_column(Text)
    leadership: Mapped[str | None] = mapped_column(Text)
    communication: Mapped[str | None] = mapped_column(Text)
    problem_solving: Mapped[str | None] = mapped_column(Text)
    initiative: Mapped[str | None] = mapped_column(Text)
    manager_comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Skill(Base):
    __tablename__ = "skills"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    category: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MemberSkill(Base):
    __tablename__ = "member_skills"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), index=True)
    skill_id: Mapped[UUID] = mapped_column(ForeignKey("skills.id"))
    source_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(100))
    manager_comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class MemberSkillEvidence(Base):
    __tablename__ = "member_skill_evidences"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_skill_id: Mapped[UUID] = mapped_column(ForeignKey("member_skills.id"), index=True)
    source_type: Mapped[str] = mapped_column(String(100))
    source_id: Mapped[UUID] = mapped_column(index=True)
    evidence_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(255))
    target_name: Mapped[str | None] = mapped_column(String(255))
    target_requirements: Mapped[str | None] = mapped_column(Text)
    emphasis_points: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(String(100))
    output_format: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(100))
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class RecommendationVersion(Base):
    __tablename__ = "recommendation_versions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recommendation_id: Mapped[UUID] = mapped_column(ForeignKey("recommendations.id"), index=True)
    version_no: Mapped[int] = mapped_column()
    version_type: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class RecommendationEvidence(Base):
    __tablename__ = "recommendation_evidences"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    recommendation_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("recommendation_versions.id"), index=True
    )
    paragraph_no: Mapped[int] = mapped_column()
    source_type: Mapped[str] = mapped_column(String(100))
    source_id: Mapped[UUID] = mapped_column(index=True)
    evidence_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class RetentionPolicy(Base):
    __tablename__ = "retention_policies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    target_type: Mapped[str] = mapped_column(String(100), unique=True)
    retention_months: Mapped[int] = mapped_column(Integer)
    purge_enabled: Mapped[bool] = mapped_column(Boolean)
    require_manual_approval: Mapped[bool] = mapped_column(Boolean)
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    updated_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AiJob(Base):
    __tablename__ = "ai_jobs"
    __table_args__ = (
        Index("ix_ai_jobs_status_created_at", "status", "created_at"),
        Index("ix_ai_jobs_target", "target_type", "target_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    job_type: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[UUID] = mapped_column()
    status: Mapped[str] = mapped_column(String(100))
    requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AiAnalysis(Base):
    __tablename__ = "ai_analyses"
    __table_args__ = (Index("ix_ai_analyses_target", "target_type", "target_id", "deleted_at"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ai_job_id: Mapped[UUID] = mapped_column(ForeignKey("ai_jobs.id"), unique=True)
    target_type: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[UUID] = mapped_column()
    provider: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(255))
    prompt_version: Mapped[str] = mapped_column(String(100))
    analysis_result: Mapped[dict[str, object]] = mapped_column(JSON)
    evidence_map: Mapped[dict[str, object]] = mapped_column(JSON)
    source_snapshot: Mapped[str] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AiSetting(Base):
    __tablename__ = "ai_settings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(100))
    base_url: Mapped[str] = mapped_column(String(2048))
    model: Mapped[str] = mapped_column(String(255))
    api_key_secret_ref: Mapped[str] = mapped_column(String(255))
    timeout_seconds: Mapped[int] = mapped_column(Integer)
    max_retries: Mapped[int] = mapped_column(Integer)
    prompt_version: Mapped[str] = mapped_column(String(100))
    updated_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MarkdownImport(Base):
    __tablename__ = "markdown_imports"
    __table_args__ = (
        Index(
            "ix_markdown_imports_hash_member_project",
            "content_hash",
            "member_id",
            "project_experience_id",
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"))
    project_experience_id: Mapped[UUID] = mapped_column(ForeignKey("project_experiences.id"))
    project_report_id: Mapped[UUID | None] = mapped_column(ForeignKey("project_reports.id"))
    original_file_name: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64))
    file_storage_key: Mapped[str | None] = mapped_column(String(2048))
    file_retained: Mapped[bool] = mapped_column(Boolean)
    template_version: Mapped[str] = mapped_column(String(100))
    import_status: Mapped[str] = mapped_column(String(100))
    imported_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MarkdownImportWarning(Base):
    __tablename__ = "markdown_import_warnings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    markdown_import_id: Mapped[UUID] = mapped_column(ForeignKey("markdown_imports.id"), index=True)
    warning_code: Mapped[str] = mapped_column(String(100))
    field_name: Mapped[str | None] = mapped_column(String(100))
    source_text: Mapped[str | None] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    resolution_status: Mapped[str] = mapped_column(String(100))
    resolved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_target_changed_at", "target_type", "target_id", "changed_at"),
        Index("ix_audit_logs_changed_by_changed_at", "changed_by", "changed_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    target_type: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[UUID] = mapped_column()
    action: Mapped[str] = mapped_column(String(100))
    before_data: Mapped[dict[str, object] | None] = mapped_column(JSON)
    after_data: Mapped[dict[str, object] | None] = mapped_column(JSON)
    changed_fields: Mapped[dict[str, object] | None] = mapped_column(JSON)
    changed_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    request_id: Mapped[UUID | None] = mapped_column()
    reason: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
