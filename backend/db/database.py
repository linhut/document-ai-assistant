# This file is part of the Official Document AI Assistant.
# (c) 2026 Jose AI (https://www.linhut.cn)
# Licensed under the MIT License. See the LICENSE file for details.
"""
SQLAlchemy database engine, session factory, and table initialization.

Configuration:
- WAL mode for concurrent read/write performance
- Retry logic for SQLITE_BUSY / database is locked errors
- Singleton engine with connection pooling
"""
import time
import functools
from typing import Callable, Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.exc import OperationalError

from config import DATABASE_URL


# SQLITE_BUSY retry configuration
_DB_RETRY_ATTEMPTS = 5
_DB_RETRY_DELAY = 0.05  # initial delay in seconds (exponential backoff)


def _retry_on_locked(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: retry on 'database is locked' errors with exponential backoff."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        last_exc = None
        delay = _DB_RETRY_DELAY
        for attempt in range(_DB_RETRY_ATTEMPTS):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if "database is locked" in str(e).lower() or "sqlite_busy" in str(e).lower():
                    last_exc = e
                    if attempt < _DB_RETRY_ATTEMPTS - 1:
                        time.sleep(delay)
                        delay *= 2  # exponential backoff
                        continue
                raise
        raise last_exc  # type: ignore[misc]
    return wrapper


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    echo=False,
)


@event.listens_for(engine, "connect")
def _set_wal_mode(dbapi_connection, connection_record):
    """Enable WAL (Write-Ahead Log) mode for better concurrent read/write."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables if they do not exist."""
    from db.models import Document, DocumentVersion, CheckResult, AIConfig, Rule  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session (with retry on lock)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

