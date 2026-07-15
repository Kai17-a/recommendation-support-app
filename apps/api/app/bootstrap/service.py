import re
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.models import Department, User, UserRole, UserStatus

DEPARTMENT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


class BootstrapValidationError(ValueError):
    """安全に初期データを更新できない場合のエラー。"""


@dataclass(frozen=True)
class BootstrapResult:
    department_id: UUID
    department_action: str
    user_id: UUID
    user_action: str


def bootstrap_user(
    session: Session,
    *,
    department_code: str,
    department_name: str,
    user_name: str,
    email: str,
    oidc_subject: str,
    role: str,
    status: str,
) -> BootstrapResult:
    """部署とOIDC操作者を単一トランザクションで冪等に登録・更新する。"""
    normalized_code = department_code.strip()
    normalized_department_name = department_name.strip()
    normalized_user_name = user_name.strip()
    normalized_email = email.strip().lower()
    normalized_subject = oidc_subject.strip()

    if not DEPARTMENT_CODE_PATTERN.fullmatch(normalized_code):
        raise BootstrapValidationError(
            "department-codeは英数字で始まる100文字以内の英数字・ピリオド・ハイフン・アンダースコアにしてください。"
        )
    _require_text("department-name", normalized_department_name, 255)
    _require_text("user-name", normalized_user_name, 255)
    _require_text("email", normalized_email, 255)
    if "@" not in normalized_email:
        raise BootstrapValidationError("emailの形式が不正です。")
    _require_text("oidc-subject", normalized_subject, 255)

    try:
        parsed_role = UserRole(role)
    except ValueError as error:
        raise BootstrapValidationError(
            f"roleは{', '.join(item.value for item in UserRole)}のいずれかにしてください。"
        ) from error
    try:
        parsed_status = UserStatus(status)
    except ValueError as error:
        raise BootstrapValidationError(
            f"statusは{', '.join(item.value for item in UserStatus)}のいずれかにしてください。"
        ) from error

    department = session.scalar(
        select(Department).where(Department.code == normalized_code).with_for_update()
    )
    if department is None:
        department = Department(code=normalized_code, name=normalized_department_name)
        session.add(department)
        session.flush()
        department_action = "created"
    else:
        department.name = normalized_department_name
        department_action = "updated"

    user = session.scalar(
        select(User).where(func.lower(User.email) == normalized_email).with_for_update()
    )
    subject_owner = session.scalar(
        select(User).where(User.oidc_subject == normalized_subject).with_for_update()
    )
    if subject_owner is not None and (user is None or subject_owner.id != user.id):
        raise BootstrapValidationError("oidc-subjectは別の操作者に登録済みです。")

    if user is None:
        user = User(
            department_id=department.id,
            name=normalized_user_name,
            email=normalized_email,
            oidc_subject=normalized_subject,
            role=parsed_role,
            status=parsed_status,
        )
        session.add(user)
        session.flush()
        user_action = "created"
    else:
        user.department_id = department.id
        user.name = normalized_user_name
        user.email = normalized_email
        user.oidc_subject = normalized_subject
        user.role = parsed_role
        user.status = parsed_status
        user_action = "updated"

    session.commit()
    return BootstrapResult(
        department_id=department.id,
        department_action=department_action,
        user_id=user.id,
        user_action=user_action,
    )


def _require_text(field: str, value: str, max_length: int) -> None:
    if not value:
        raise BootstrapValidationError(f"{field}は必須です。")
    if len(value) > max_length:
        raise BootstrapValidationError(f"{field}は{max_length}文字以内にしてください。")
