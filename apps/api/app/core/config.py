from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """実行環境から読み込むアプリケーション設定。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://app:change-me-for-local-development@localhost:5432/recommendation_support"


settings = Settings()
