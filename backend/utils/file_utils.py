"""
File utilities: hashing, safe saving, temp paths.
"""
import hashlib
import shutil
from pathlib import Path


def file_sha256(path: Path) -> str:
    """Compute the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename(name: str) -> str:
    """Return a filesystem-safe version of a filename."""
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in name)


def ensure_dir(path: Path) -> Path:
    """Create directory (and parents) if it doesn't exist, then return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_to_dir(src: Path, dest_dir: Path) -> Path:
    """Copy a file into a destination directory, returning the new path."""
    ensure_dir(dest_dir)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    return dest
