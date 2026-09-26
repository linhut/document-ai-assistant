# (c) 2026 Jose AI (https://www.linhut.cn)
# https://github.com/linhut/document-ai-assistant
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
from utils.logger import logger


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


def _ensure_column(table: str, column: str, ddl: str) -> None:
    """轻量列迁移：旧库缺列时补充（幂等，不重建表）。"""
    with engine.connect() as conn:
        _ensure_column_with(conn, table, column, ddl)


def _ensure_column_with(conn, table: str, column: str, ddl: str) -> None:
    """在给定连接的上下文中补充缺失列（幂等），供版本化迁移调用。"""
    cols = [row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")]
    if column not in cols:
        conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


# 版本化迁移表：key=目标版本号（从 1 开始），value=该版本需要执行的增量变更。
# 变更 spec 支持两种形式：
#   - tuple (table, column, ddl) → 走幂等补列（列已存在则跳过）
#   - str（原生 SQL）→ 直接执行（需自行保证幂等）
# 迁移版本记录在 SQLite PRAGMA user_version，升级/重放均安全。
_MIGRATIONS: dict[int, list[tuple[str, str, str] | str]] = {
    1: [
        ("check_results", "standard_ref", "VARCHAR(64)"),
    ],
    # 新增迁移示例（发布新字段时取消注释并递增版本号）：
    # 2: [
    #     ("documents", "version", "INT DEFAULT 1"),
    # ],
}


def _get_user_version(conn) -> int:
    return int(conn.exec_driver_sql("PRAGMA user_version").fetchone()[0])


def _run_migrations() -> None:
    """依次执行未应用过的迁移，并推进 PRAGMA user_version。"""
    with engine.connect() as conn:
        current = _get_user_version(conn)
        for version in sorted(_MIGRATIONS):
            if version <= current:
                continue
            for spec in _MIGRATIONS[version]:
                if isinstance(spec, str):
                    conn.exec_driver_sql(spec)
                else:
                    table, column, ddl = spec
                    _ensure_column_with(conn, table, column, ddl)
            conn.exec_driver_sql(f"PRAGMA user_version = {version}")
            conn.commit()
        if _get_user_version(conn) > 0:
            logger.info(f"Database migrations applied, user_version={_get_user_version(conn)}")


def init_db() -> None:
    """Create all tables if they do not exist, then apply versioned migrations."""
    from db.models import Document, DocumentVersion, CheckResult, AIConfig, Rule  # noqa: F401

    Base.metadata.create_all(bind=engine)
    # 版本化迁移（兼容旧库增量补列，幂等可重入）
    _run_migrations()


def get_db():
    """FastAPI dependency that yields a DB session (with retry on lock)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
