from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.bootstrap.cli import run
from app.bootstrap.service import BootstrapValidationError, bootstrap_user
from app.infrastructure.models import Base, Department, User, UserRole, UserStatus


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


def _bootstrap(session: Session, **overrides: str):
    values = {
        "department_code": "platform",
        "department_name": "プラットフォーム部",
        "user_name": "運用管理者",
        "email": "operator@example.com",
        "oidc_subject": "idp-operator-001",
        "role": "system_operator",
        "status": "active",
    }
    values.update(overrides)
    return bootstrap_user(session, **values)


def test_bootstrap_is_idempotent_and_updates_mutable_fields(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        first = _bootstrap(session)
    with session_factory() as session:
        second = _bootstrap(
            session,
            department_name="基盤部",
            user_name="運用担当者",
            role="manager",
            status="inactive",
        )
        departments = session.scalars(select(Department)).all()
        users = session.scalars(select(User)).all()

    assert first.department_action == "created"
    assert first.user_action == "created"
    assert second.department_action == "updated"
    assert second.user_action == "updated"
    assert second.department_id == first.department_id
    assert second.user_id == first.user_id
    assert len(departments) == 1
    assert departments[0].name == "基盤部"
    assert len(users) == 1
    assert users[0].name == "運用担当者"
    assert users[0].role is UserRole.MANAGER
    assert users[0].status is UserStatus.INACTIVE


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("department_code", "invalid code"),
        ("department_name", ""),
        ("role", "administrator"),
        ("status", "disabled"),
    ],
)
def test_bootstrap_validates_department_role_and_status(
    session_factory: sessionmaker[Session], field: str, value: str
) -> None:
    with session_factory() as session, pytest.raises(BootstrapValidationError):
        _bootstrap(session, **{field: value})


def test_bootstrap_rejects_oidc_subject_owned_by_another_user(
    session_factory: sessionmaker[Session],
) -> None:
    with session_factory() as session:
        _bootstrap(session)
        with pytest.raises(BootstrapValidationError):
            _bootstrap(session, email="other@example.com")

        assert len(session.scalars(select(User)).all()) == 1


def test_cli_registers_inactive_manager_without_outputting_identifiers(
    session_factory: sessionmaker[Session], capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = run(
        [
            "--department-code",
            "sales",
            "--department-name",
            "営業部",
            "--user-name",
            "営業管理者",
            "--email",
            "manager@example.com",
            "--oidc-subject",
            "sensitive-subject-value",
            "--role",
            "manager",
            "--status",
            "inactive",
        ],
        session_factory=session_factory,
    )

    output = capsys.readouterr()
    assert exit_code == 0
    assert "sensitive-subject-value" not in output.out
    assert "manager@example.com" not in output.out
    with session_factory() as session:
        user = session.scalar(select(User))
        assert user is not None
        assert user.status is UserStatus.INACTIVE
