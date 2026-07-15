from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
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
