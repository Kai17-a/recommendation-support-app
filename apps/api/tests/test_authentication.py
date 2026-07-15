import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.security import HTTPAuthorizationCredentials
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.infrastructure.models import Base, Department, User, UserRole, UserStatus
from app.security import authentication
from app.security.authentication import OidcTokenVerifier, get_current_user

ISSUER = "https://idp.example.com"
AUDIENCE = "recommendation-support-api"
KEY_ID = "signing-key-1"


def _key_material() -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk.update({"kid": KEY_ID, "alg": "RS256", "use": "sig"})
    return private_key, jwk


def _token(private_key: rsa.RSAPrivateKey, **overrides: Any) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "operator-123",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "email": "manager@example.com",
        "email_verified": True,
    }
    claims.update(overrides)
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": KEY_ID})


def _transport(jwk: dict[str, Any], calls: list[str]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path == "/.well-known/openid-configuration":
            return httpx.Response(200, json={"jwks_uri": f"{ISSUER}/jwks"})
        if request.url.path == "/jwks":
            return httpx.Response(200, json={"keys": [jwk]})
        return httpx.Response(404)

    return httpx.MockTransport(handler)


@pytest.mark.anyio
async def test_oidc_verifier_validates_signature_and_caches_jwks() -> None:
    private_key, jwk = _key_material()
    calls: list[str] = []
    verifier = OidcTokenVerifier(
        issuer_url=ISSUER,
        audience=AUDIENCE,
        algorithms=("RS256",),
        jwks_cache_seconds=300,
        clock_skew_seconds=0,
        transport=_transport(jwk, calls),
    )

    first = await verifier.verify(_token(private_key))
    second = await verifier.verify(_token(private_key))

    assert first["sub"] == "operator-123"
    assert second["email"] == "manager@example.com"
    assert calls == ["/.well-known/openid-configuration", "/jwks"]


@pytest.mark.anyio
async def test_oidc_verifier_rejects_wrong_audience() -> None:
    private_key, jwk = _key_material()
    verifier = OidcTokenVerifier(
        issuer_url=ISSUER,
        audience=AUDIENCE,
        algorithms=("RS256",),
        jwks_cache_seconds=300,
        clock_skew_seconds=0,
        transport=_transport(jwk, []),
    )

    with pytest.raises(ApiError) as captured:
        await verifier.verify(_token(private_key, aud="different-api"))

    assert captured.value.status_code == 401
    assert captured.value.code == "INVALID_ACCESS_TOKEN"


class StaticVerifier:
    def __init__(self, claims: dict[str, Any]) -> None:
        self.claims = claims

    async def verify(self, _: str) -> dict[str, Any]:
        return self.claims


@pytest.mark.anyio
async def test_current_user_links_verified_email_to_oidc_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    department_id = uuid4()
    user_id = uuid4()
    with Session(engine) as session:
        session.add(Department(id=department_id, name="開発", code="dev"))
        session.add(
            User(
                id=user_id,
                department_id=department_id,
                name="管理者",
                email="manager@example.com",
                role=UserRole.MANAGER,
                status=UserStatus.ACTIVE,
            )
        )
        session.commit()
        monkeypatch.setattr(
            authentication,
            "token_verifier",
            StaticVerifier(
                {
                    "sub": "operator-123",
                    "email": "manager@example.com",
                    "email_verified": True,
                }
            ),
        )

        current_user = await get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"), session
        )

        assert current_user.id == user_id
        assert current_user.department_id == department_id
        assert session.scalar(select(User.oidc_subject).where(User.id == user_id)) == "operator-123"


@pytest.mark.anyio
async def test_current_user_rejects_unregistered_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite+pysqlite://")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(
        authentication,
        "token_verifier",
        StaticVerifier({"sub": "unknown", "email": "unknown@example.com"}),
    )

    with Session(engine) as session, pytest.raises(ApiError) as captured:
        await get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"), session
        )

    assert captured.value.status_code == 403
    assert captured.value.code == "USER_NOT_REGISTERED"
