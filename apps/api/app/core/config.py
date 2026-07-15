from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """実行環境から読み込むアプリケーション設定。"""

    model_config = SettingsConfigDict(env_file=REPOSITORY_ROOT / ".env", extra="ignore")

    database_url: str = "postgresql+psycopg://app:change-me-for-local-development@localhost:5432/recommendation_support"
    redis_url: str = "redis://localhost:6379/0"
    oidc_issuer_url: str | None = None
    oidc_audience: str = "recommendation-support-api"
    oidc_algorithms: str = "RS256"
    oidc_jwks_cache_seconds: int = 300
    oidc_clock_skew_seconds: int = 30
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:3001"
    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_region: str = "ap-northeast-1"
    s3_markdown_bucket: str = "recommendation-support-markdown"
    s3_access_key_id: str | None = "minioadmin"
    s3_secret_access_key: str | None = "change-me-for-local-development"
    s3_server_side_encryption: str | None = None
    log_level: str = "INFO"
    max_request_body_bytes: int = 12 * 1024 * 1024


settings = Settings()
