from datetime import date, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
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
