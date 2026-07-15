from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.errors import ApiError
from app.infrastructure.models import (
    Base,
    Department,
    Member,
    MemberStatus,
    UserRole,
)
from app.security.authentication import CurrentUser
from app.security.authorization import AccessControl


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as value:
        yield value
    Base.metadata.drop_all(engine)
    engine.dispose()


def current_user(*, department_id, role=UserRole.MANAGER) -> CurrentUser:
    return CurrentUser(
        id=uuid4(),
        department_id=department_id,
        role=role,
        name="操作者",
        email="operator@example.com",
    )


def test_manager_can_access_own_department_and_direct_reports(session: Session) -> None:
    own_department = Department(name="開発", code="DEV")
    other_department = Department(name="営業", code="SALES")
    session.add_all([own_department, other_department])
    session.flush()
    user = current_user(department_id=own_department.id)
    same_department = Member(
        department_id=own_department.id,
        manager_user_id=uuid4(),
        name="同部署",
        status=MemberStatus.ACTIVE,
    )
    direct_report = Member(
        department_id=other_department.id,
        manager_user_id=user.id,
        name="直属",
        status=MemberStatus.ACTIVE,
    )
    session.add_all([same_department, direct_report])
    session.commit()

    access = AccessControl(session, user)

    assert access.ensure_member(same_department.id).id == same_department.id
    assert access.ensure_member(direct_report.id).id == direct_report.id


def test_manager_cannot_access_other_department_member(session: Session) -> None:
    own_department = Department(name="開発", code="DEV")
    other_department = Department(name="営業", code="SALES")
    session.add_all([own_department, other_department])
    session.flush()
    user = current_user(department_id=own_department.id)
    member = Member(
        department_id=other_department.id,
        manager_user_id=uuid4(),
        name="他部署",
        status=MemberStatus.ACTIVE,
    )
    session.add(member)
    session.commit()

    with pytest.raises(ApiError) as error:
        AccessControl(session, user).ensure_member(member.id)

    assert error.value.status_code == 403
    assert error.value.code == "FORBIDDEN"


def test_system_operator_is_limited_to_admin_operations(session: Session) -> None:
    department = Department(name="運用", code="OPS")
    session.add(department)
    session.flush()
    user = current_user(department_id=department.id, role=UserRole.SYSTEM_OPERATOR)
    access = AccessControl(session, user)

    access.require_system_operator()
    with pytest.raises(ApiError) as error:
        access.require_manager()

    assert error.value.status_code == 403
