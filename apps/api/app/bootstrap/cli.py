import argparse
import json
import sys
from collections.abc import Callable, Sequence

from sqlalchemy.orm import Session

from app.bootstrap.service import BootstrapValidationError, bootstrap_user
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import UserRole, UserStatus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="初期部署とOIDC操作者を冪等に登録・更新します。")
    parser.add_argument("--department-code", required=True)
    parser.add_argument("--department-name", required=True)
    parser.add_argument("--user-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--oidc-subject", required=True)
    parser.add_argument("--role", required=True, choices=[item.value for item in UserRole])
    parser.add_argument(
        "--status",
        default=UserStatus.ACTIVE.value,
        choices=[item.value for item in UserStatus],
    )
    return parser


def run(
    argv: Sequence[str] | None = None,
    *,
    session_factory: Callable[[], Session] = SessionLocal,
) -> int:
    args = build_parser().parse_args(argv)
    with session_factory() as session:
        try:
            result = bootstrap_user(
                session,
                department_code=args.department_code,
                department_name=args.department_name,
                user_name=args.user_name,
                email=args.email,
                oidc_subject=args.oidc_subject,
                role=args.role,
                status=args.status,
            )
        except BootstrapValidationError as error:
            session.rollback()
            print(f"bootstrap failed: {error}", file=sys.stderr)
            return 2
        except Exception:
            session.rollback()
            raise

    print(
        json.dumps(
            {
                "department_id": str(result.department_id),
                "department_action": result.department_action,
                "user_id": str(result.user_id),
                "user_action": result.user_action,
            }
        )
    )
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
