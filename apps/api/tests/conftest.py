from collections.abc import Generator
from uuid import UUID

import pytest

from app.api.routes.admin import require_admin
from app.infrastructure.models import UserRole
from app.main import app
from app.security.authentication import CurrentUser, get_current_user


@pytest.fixture(autouse=True)
def authenticated_operator() -> Generator[None]:
    """API tests run with an explicit authenticated manager unless overridden."""

    async def override_current_user() -> CurrentUser:
        return CurrentUser(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            department_id=UUID("00000000-0000-0000-0000-000000000002"),
            role=UserRole.MANAGER,
            name="テスト操作者",
            email="operator@example.com",
        )

    async def override_admin() -> None:
        return None

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[require_admin] = override_admin
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(require_admin, None)
