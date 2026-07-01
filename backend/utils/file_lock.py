"""
File lock mechanism for concurrent document processing.

Provides a cross-process file lock using lock files in a temp directory.
Prevents multiple processes from modifying the same document simultaneously.

Usage:
    with file_lock(doc_id=42) as locked:
        if locked:
            # process document...
        else:
            # another process is already handling this document
"""
import os
import time
import atexit
import tempfile
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator

from utils.logger import logger

# --- Configuration ---
_LOCK_DIR = Path(tempfile.gettempdir()) / ".doc_optimizer_locks"
_LOCK_TIMEOUT = 300       # 5 minutes max lock hold time
_LOCK_RETRY_INTERVAL = 0.1  # 100ms between lock attempts
_LOCK_RETRY_MAX = 50       # 5 seconds total retry (50 × 100ms)


def _lock_path(doc_id: int) -> Path:
    """Get the lock file path for a given document ID."""
    _LOCK_DIR.mkdir(parents=True, exist_ok=True)
    return _LOCK_DIR / f"doc_{doc_id}.lock"


def _is_lock_stale(lock_path: Path) -> bool:
    """Check if a lock file is older than the timeout threshold."""
    try:
        age = time.time() - lock_path.stat().st_mtime
        return age > _LOCK_TIMEOUT
    except (OSError, ValueError):
        return False


def _cleanup_stale_locks() -> None:
    """Remove all stale lock files on startup."""
    try:
        if _LOCK_DIR.exists():
            for lock_file in _LOCK_DIR.glob("doc_*.lock"):
                if _is_lock_stale(lock_file):
                    lock_file.unlink()
                    logger.info(f"Cleaned stale lock: {lock_file.name}")
    except Exception as e:
        logger.warning(f"Failed to clean stale locks: {e}")


def acquire_lock(doc_id: int, blocking: bool = True) -> bool:
    """
    Attempt to acquire a lock for the given document ID.

    Args:
        doc_id: The document ID to lock.
        blocking: If True, retry for up to _LOCK_RETRY_MAX attempts.

    Returns:
        True if the lock was acquired, False otherwise.
    """
    lock_path = _lock_path(doc_id)
    pid = os.getpid()

    retries = _LOCK_RETRY_MAX if blocking else 1
    for attempt in range(retries):
        try:
            # Try to create the lock file exclusively
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(str(pid))
            return True
        except FileExistsError:
            # Lock already exists — check if stale
            if _is_lock_stale(lock_path):
                try:
                    lock_path.unlink()
                    continue  # retry after removing stale lock
                except OSError:
                    pass

            if blocking and attempt < retries - 1:
                time.sleep(_LOCK_RETRY_INTERVAL)
                continue
            return False
        except OSError:
            return False

    return False


def release_lock(doc_id: int) -> None:
    """Release a previously acquired lock for the given document ID."""
    lock_path = _lock_path(doc_id)
    try:
        if lock_path.exists():
            lock_path.unlink()
    except OSError as e:
        logger.warning(f"Failed to release lock for doc {doc_id}: {e}")


@contextmanager
def file_lock(doc_id: int, blocking: bool = True) -> Iterator[bool]:
    """
    Context manager for file-based locking.

    Example:
        with file_lock(42) as acquired:
            if acquired:
                # process document 42
            else:
                # document 42 is being processed elsewhere
                return {"error": "Document is being processed"}

    Args:
        doc_id: Document ID to lock.
        blocking: If True, wait and retry for up to ~5 seconds.

    Yields:
        True if lock was acquired, False otherwise.
    """
    acquired = acquire_lock(doc_id, blocking=blocking)
    try:
        yield acquired
    finally:
        if acquired:
            release_lock(doc_id)


# Clean up stale locks on import (startup)
_cleanup_stale_locks()

# Ensure all locks are released on interpreter exit
atexit.register(lambda: _cleanup_stale_locks())
