"""
Database backup utility.

Creates timestamped backups of the SQLite database to APP_DATA_DIR/backups/.
Keeps a configurable number of recent backups and auto-prunes old ones.

Usage:
    from utils.db_backup import backup_database
    backup_database()  # one-shot backup

For periodic backups, call from a background task or cron-equivalent.
"""
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

from config import APP_DATA_DIR
from utils.logger import logger

# --- Configuration ---
BACKUP_DIR = APP_DATA_DIR / "backups"
MAX_BACKUPS = 14           # keep 14 most recent backups (2 weeks at daily)
BACKUP_INTERVAL_HOURS = 6  # minimum gap between backups


def _get_db_path() -> Path | None:
    """Resolve the actual database file path from DATABASE_URL."""
    import os
    raw = os.getenv("DATABASE_URL", f"sqlite:///{APP_DATA_DIR / 'app.db'}")
    # sqlite:///path
    if raw.startswith("sqlite:///"):
        return Path(raw[len("sqlite:///"):])
    return None


def backup_database() -> Path | None:
    """
    Create a timestamped backup of the current database.
    Returns the backup path, or None if skipped/failed.
    """
    db_path = _get_db_path()
    if not db_path or not db_path.exists():
        logger.warning(f"Database backup skipped: db not found at {db_path}")
        return None

    # Ensure backup directory exists
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Check if we backed up recently (avoid spamming on frequent restarts)
    existing = sorted(BACKUP_DIR.glob("app_backup_*.db"))
    if existing:
        latest = existing[-1]
        try:
            # Extract timestamp from filename: app_backup_20260630_210000.db
            ts_str = latest.stem.replace("app_backup_", "")
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            if datetime.now() - ts < timedelta(hours=BACKUP_INTERVAL_HOURS):
                logger.info(f"Database backup skipped: last backup was less than {BACKUP_INTERVAL_HOURS}h ago")
                return None
        except (ValueError, IndexError):
            pass  # if filename format doesn't match, just create new backup

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"app_backup_{timestamp}.db"

    try:
        # For SQLite WAL mode, also copy -wal and -shm files if they exist
        shutil.copy2(db_path, backup_path)
        for ext in (".db-wal", ".db-shm"):
            wal_file = db_path.parent / (db_path.name + ext)
            if wal_file.exists():
                shutil.copy2(wal_file, BACKUP_DIR / f"app_backup_{timestamp}.db{ext}")

        logger.info(f"Database backed up to {backup_path}")

        # Prune old backups
        _prune_old_backups()

        return backup_path
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return None


def _prune_old_backups() -> None:
    """Remove backups beyond MAX_BACKUPS, keeping the most recent ones."""
    backups = sorted(BACKUP_DIR.glob("app_backup_*.db"))
    if len(backups) <= MAX_BACKUPS:
        return

    to_delete = backups[:-MAX_BACKUPS]
    for old in to_delete:
        try:
            old.unlink()
            # Also remove associated WAL/SHM files
            for ext in (".db-wal", ".db-shm"):
                extra = old.parent / (old.name + ext)
                if extra.exists():
                    extra.unlink()
        except Exception as e:
            logger.warning(f"Failed to remove old backup {old}: {e}")

    logger.info(f"Pruned {len(to_delete)} old backup(s), kept {MAX_BACKUPS}")


def list_backups() -> list[dict]:
    """List existing backups with metadata."""
    backups = sorted(BACKUP_DIR.glob("app_backup_*.db"), reverse=True)
    result = []
    for b in backups:
        try:
            ts_str = b.stem.replace("app_backup_", "")
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            size_kb = b.stat().st_size / 1024
            result.append({
                "filename": b.name,
                "timestamp": ts.isoformat(),
                "size_kb": round(size_kb, 1),
            })
        except (ValueError, IndexError):
            result.append({
                "filename": b.name,
                "timestamp": "unknown",
                "size_kb": round(b.stat().st_size / 1024, 1),
            })
    return result


def ensure_startup_backup() -> None:
    """Call on app startup to ensure an initial backup exists."""
    backup_database()
