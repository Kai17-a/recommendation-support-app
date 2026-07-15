from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """実行環境から読み込むアプリケーション設定。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://app:change-me-for-local-development@localhost:5432/recommendation_support"
    redis_url: str = "redis://localhost:6379/0"
    oidc_issuer_url: str | None = None
    oidc_audience: str = "recommendation-support-api"
    oidc_algorithms: str = "RS256"
    oidc_jwks_cache_seconds: int = 300
    oidc_clock_skew_seconds: int = 30


settings = Settings()
