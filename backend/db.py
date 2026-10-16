from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


# Open a connection with row access and foreign-key checks.
def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Commit a database operation and always release its connection.
@contextmanager
def open_database(database_path: Path):
    connection = connect(database_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


# Create missing tables without replacing existing records.
def initialise_database(database_path: Path) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    connection = connect(database_path)
    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        connection.commit()
    finally:
        connection.close()
