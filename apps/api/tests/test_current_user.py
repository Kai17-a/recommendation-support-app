import httpx
import pytest

from app.main import app


@pytest.mark.anyio
async def test_current_user_returns_authenticated_user() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": "00000000-0000-0000-0000-000000000001",
        "department_id": "00000000-0000-0000-0000-000000000002",
        "role": "manager",
        "name": "テスト操作者",
        "email": "operator@example.com",
    }
