from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

from config import Config


# Copy the SQLite database and uploaded evidence to a named folder.
def backup(destination: Path) -> None:
    if not Path(Config.DATABASE_PATH).exists():
        raise FileNotFoundError("Database has not been initialised.")
    if destination.exists():
        raise FileExistsError(f"Backup destination already exists: {destination}")
    destination.mkdir(parents=True)
    source = sqlite3.connect(Config.DATABASE_PATH)
    target = sqlite3.connect(destination / "greencert.db")
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    if Path(Config.UPLOAD_DIR).exists():
        shutil.copytree(Config.UPLOAD_DIR, destination / "uploads")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/backup_data.py backups/<name>")
    backup(Path(sys.argv[1]))
