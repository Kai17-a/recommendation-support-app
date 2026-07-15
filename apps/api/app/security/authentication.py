from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import httpx
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWK
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ApiError
from app.infrastructure.database import get_session
from app.infrastructure.models import User, UserRole, UserStatus


@dataclass(frozen=True)
class CurrentUser:
    """認証済み操作者としてAPI内部で利用する最小属性。"""

    id: UUID
    department_id: UUID
    role: UserRole
    name: str
    email: str


class OidcTokenVerifier:
    """OIDC DiscoveryとJWKSを用いてアクセストークンを検証する。"""

    def __init__(
        self,
        *,
        issuer_url: str | None,
        audience: str,
        algorithms: tuple[str, ...],
        jwks_cache_seconds: int,
        clock_skew_seconds: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._issuer_url = issuer_url.rstrip("/") if issuer_url else None
        self._audience = audience
        self._algorithms = algorithms
        self._jwks_cache_duration = timedelta(seconds=jwks_cache_seconds)
        self._clock_skew_seconds = clock_skew_seconds
        self._transport = transport
        self._jwks: dict[str, Any] | None = None
        self._jwks_expires_at: datetime | None = None

    async def verify(self, token: str) -> dict[str, Any]:
        if self._issuer_url is None:
            raise ApiError(
                status_code=503,
                code="OIDC_NOT_CONFIGURED",
                message="OIDC認証が設定されていません。",
            )
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            algorithm = header.get("alg")
            if not isinstance(kid, str) or algorithm not in self._algorithms:
                raise InvalidTokenError("unsupported token header")
            jwk = await self._find_jwk(kid)
            key = PyJWK.from_dict(jwk, algorithm=algorithm).key
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self._algorithms),
                audience=self._audience,
                issuer=self._issuer_url,
                leeway=self._clock_skew_seconds,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
            )
        except (InvalidTokenError, KeyError, TypeError, ValueError) as error:
            raise _invalid_token_error() from error
        return claims

    async def _find_jwk(self, kid: str) -> dict[str, Any]:
        jwks = await self._get_jwks()
        for key in jwks.get("keys", []):
            if isinstance(key, dict) and key.get("kid") == kid:
                return key
        # 鍵ローテーション直後を考慮してキャッシュを一度だけ更新する。
        self._jwks = None
        jwks = await self._get_jwks()
        for key in jwks.get("keys", []):
            if isinstance(key, dict) and key.get("kid") == kid:
                return key
        raise InvalidTokenError("signing key not found")

    async def _get_jwks(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        if self._jwks is not None and self._jwks_expires_at is not None:
            if now < self._jwks_expires_at:
                return self._jwks

        discovery_url = f"{self._issuer_url}/.well-known/openid-configuration"
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=5) as client:
                discovery_response = await client.get(discovery_url)
                discovery_response.raise_for_status()
                jwks_uri = discovery_response.json()["jwks_uri"]
                jwks_response = await client.get(jwks_uri)
                jwks_response.raise_for_status()
                jwks = jwks_response.json()
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise ApiError(
                status_code=503,
                code="OIDC_PROVIDER_UNAVAILABLE",
                message="OIDCプロバイダーから検証情報を取得できません。",
            ) from error
        if not isinstance(jwks, dict) or not isinstance(jwks.get("keys"), list):
            raise ApiError(
                status_code=503,
                code="OIDC_PROVIDER_UNAVAILABLE",
                message="OIDCプロバイダーの検証情報が不正です。",
            )
        self._jwks = jwks
        self._jwks_expires_at = now + self._jwks_cache_duration
        return jwks


bearer_scheme = HTTPBearer(auto_error=False)
token_verifier = OidcTokenVerifier(
    issuer_url=settings.oidc_issuer_url,
    audience=settings.oidc_audience,
    algorithms=tuple(item.strip() for item in settings.oidc_algorithms.split(",") if item.strip()),
    jwks_cache_seconds=settings.oidc_jwks_cache_seconds,
    clock_skew_seconds=settings.oidc_clock_skew_seconds,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(
            status_code=401,
            code="AUTHENTICATION_REQUIRED",
            message="Bearerアクセストークンが必要です。",
        )
    claims = await token_verifier.verify(credentials.credentials)
    subject = claims["sub"]
    if not isinstance(subject, str) or not subject:
        raise _invalid_token_error()

    user = session.scalar(select(User).where(User.oidc_subject == subject))
    if user is None:
        user = _link_existing_user(session, claims, subject)
    if user is None:
        raise ApiError(
            status_code=403,
            code="USER_NOT_REGISTERED",
            message="認証された利用者はシステムに登録されていません。",
        )
    if user.status != UserStatus.ACTIVE:
        raise ApiError(
            status_code=403,
            code="USER_INACTIVE",
            message="利用者アカウントは無効です。",
        )
    return CurrentUser(
        id=user.id,
        department_id=user.department_id,
        role=user.role,
        name=user.name,
        email=user.email,
    )


def _link_existing_user(session: Session, claims: dict[str, Any], subject: str) -> User | None:
    email = claims.get("email")
    email_verified = claims.get("email_verified")
    if not isinstance(email, str) or email_verified is not True:
        return None
    user = session.scalar(
        select(User).where(User.email == email, User.oidc_subject.is_(None)).with_for_update()
    )
    if user is None:
        return None
    user.oidc_subject = subject
    session.commit()
    session.refresh(user)
    return user


def _invalid_token_error() -> ApiError:
    return ApiError(
        status_code=401,
        code="INVALID_ACCESS_TOKEN",
        message="アクセストークンが無効です。",
    )
