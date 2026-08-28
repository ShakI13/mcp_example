"""Helpers for building a tiny fixture SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

FIXTURE_SQL = Path(__file__).with_name("shop_fixture.sql")


def build_fixture_db(db_path: Path) -> Path:
    """Create ``db_path`` from the fixture SQL script and return the path."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    sql = FIXTURE_SQL.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
    return db_path
