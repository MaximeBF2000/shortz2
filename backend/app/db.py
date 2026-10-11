"""Database engine and session helpers."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request."""
    with SessionLocal() as session:
        yield session


@contextmanager
def session_scope() -> Iterator[Session]:
    """For worker code: a session that commits on success."""
    with SessionLocal() as session:
        yield session
        session.commit()


def create_tables() -> None:
    # Importing the models registers them on Base.metadata.
    import app.models  # noqa: F401

    # The API and the worker start together: a lock stops them racing each other.
    with engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(7428)"))
        Base.metadata.create_all(connection)
