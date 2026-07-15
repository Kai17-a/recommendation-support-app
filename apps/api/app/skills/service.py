from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Member, MemberSkill, MemberSkillEvidence, Skill
from app.security.authorization import AccessControl
from app.skills.schemas import SkillCreate, SkillUpdate


class SkillService:
    def __init__(self, session: Session, access: AccessControl | None = None) -> None:
        self.session = session
        self.access = access

    def list_for_member(self, member_id: UUID) -> list[MemberSkill]:
        self._member(member_id)
        return list(
            self.session.scalars(
                select(MemberSkill).where(
                    MemberSkill.member_id == member_id, MemberSkill.deleted_at.is_(None)
                )
            )
        )

    def create(self, member_id: UUID, c: SkillCreate) -> MemberSkill:
        self._member(member_id)
        skill = self.session.scalar(select(Skill).where(Skill.name == c.name))
        if skill is None:
            skill = Skill(name=c.name, category=c.category, description=c.description)
            self.session.add(skill)
            self.session.flush()
        row = MemberSkill(
            member_id=member_id,
            skill_id=skill.id,
            source_type=c.source_type,
            status=c.status,
            manager_comment=c.manager_comment,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def update(self, id: UUID, c: SkillUpdate) -> MemberSkill:
        row = self._get(id)
        for k, v in c.model_dump(exclude_unset=True).items():
            setattr(row, k, v)
        self.session.commit()
        self.session.refresh(row)
        return row

    def delete(self, id: UUID) -> None:
        row = self._get(id)
        row.deleted_at = datetime.now(UTC)
        self.session.commit()

    def evidences(self, id: UUID) -> list[MemberSkillEvidence]:
        self._get(id)
        return list(
            self.session.scalars(
                select(MemberSkillEvidence).where(
                    MemberSkillEvidence.member_skill_id == id,
                    MemberSkillEvidence.deleted_at.is_(None),
                )
            )
        )

    def _member(self, id: UUID) -> Member:
        if self.access is not None:
            return self.access.ensure_member(id)
        x = self.session.scalar(select(Member).where(Member.id == id, Member.deleted_at.is_(None)))
        if x is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="メンバーが見つかりません。")
        return x

    def _get(self, id: UUID) -> MemberSkill:
        x = self.session.scalar(
            select(MemberSkill).where(MemberSkill.id == id, MemberSkill.deleted_at.is_(None))
        )
        if x is None:
            raise ApiError(status_code=404, code="NOT_FOUND", message="スキルが見つかりません。")
        self._member(x.member_id)
        return x
