"""Read-only SQLite access for the shop MCP server."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class DatabaseError(Exception):
    """Recoverable database configuration or access error."""


def _missing_db_message(path: Path | None) -> str:
    if path is None:
        return (
            "Database unavailable: set SHOP_DB_PATH to a readable SQLite file "
            "(for example data/shop.db), then retry."
        )
    return (
        f"Database unavailable: cannot open SHOP_DB_PATH={path}. "
        "Place the SQLite file at that path (or update SHOP_DB_PATH) and retry."
    )


def resolve_db_path(path: Path | None) -> Path:
    """Validate that ``path`` points to an existing readable file."""
    if path is None:
        raise DatabaseError(_missing_db_message(None))
    if not path.is_file():
        raise DatabaseError(_missing_db_message(path))
    return path


def _readonly_uri(path: Path) -> str:
    return path.resolve().as_uri() + "?mode=ro"


@contextmanager
def connect(path: Path) -> Iterator[sqlite3.Connection]:
    """Open a short-lived read-only SQLite connection."""
    resolved = resolve_db_path(path)
    try:
        conn = sqlite3.connect(_readonly_uri(resolved), uri=True)
    except sqlite3.Error as exc:
        raise DatabaseError(_missing_db_message(resolved)) from exc
    try:
        conn.row_factory = None
        conn.execute("PRAGMA query_only=ON")
        yield conn
    finally:
        conn.close()


def list_user_tables(conn: sqlite3.Connection) -> list[dict[str, str]]:
    rows = conn.execute(
        """
        SELECT name, type
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [{"name": name, "type": type_} for name, type_ in rows]


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
          AND name NOT LIKE 'sqlite_%'
        """,
        (table_name,),
    ).fetchone()
    return row is not None


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def describe_table(conn: sqlite3.Connection, table_name: str) -> dict[str, Any]:
    if not table_exists(conn, table_name):
        raise DatabaseError(
            f"Table not found: {table_name!r}. "
            "Call list_tables to see available tables."
        )
    # PRAGMA table_info does not accept bound parameters; table_name is validated above.
    rows = conn.execute(f"PRAGMA table_info({_quote_ident(table_name)})").fetchall()
    columns = []
    for _cid, name, col_type, notnull, _default, pk in rows:
        columns.append(
            {
                "name": name,
                "type": col_type or "",
                "nullable": not bool(notnull),
                "primary_key": bool(pk),
            }
        )
    return {"table_name": table_name, "columns": columns}


def _cell_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return value


def run_select(
    conn: sqlite3.Connection,
    sql: str,
    max_rows: int,
) -> dict[str, Any]:
    try:
        cursor = conn.execute(sql)
    except sqlite3.Error as exc:
        raise DatabaseError(f"SQLite error: {exc}") from exc

    column_names = [desc[0] for desc in (cursor.description or [])]
    fetched = cursor.fetchmany(max_rows + 1)
    truncated = len(fetched) > max_rows
    rows = fetched[:max_rows]
    serialized = [[_cell_value(cell) for cell in row] for row in rows]
    return {
        "columns": column_names,
        "rows": serialized,
        "row_count": len(serialized),
        "truncated": truncated,
    }
