from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session]:
    """リクエスト単位のDBセッションを提供する。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
