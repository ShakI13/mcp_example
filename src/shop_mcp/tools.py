"""Tool handlers for the shop MCP server (testable without a live MCP session)."""

from __future__ import annotations

from typing import Any

from shop_mcp import db
from shop_mcp.config import get_db_path
from shop_mcp.sql_guard import SqlGuardError, validate_select

DEFAULT_MAX_ROWS = 100
MIN_MAX_ROWS = 1
MAX_MAX_ROWS = 500

LIST_TABLES_DESCRIPTION = (
    "List user tables in the shop SQLite database (name and type only).\n"
    "Use this first when you need to know what data exists.\n"
    "For column details, call describe_table next.\n"
    "Read-only: never modifies the database."
)

DESCRIBE_TABLE_DESCRIPTION = (
    "Describe columns for one table (name, SQL type, nullable, primary_key).\n"
    "Use after list_tables before writing SQL for run_select_query.\n"
    "Parameter table_name must be an existing user table.\n"
    "Read-only: never modifies the database."
)

RUN_SELECT_QUERY_DESCRIPTION = (
    "Run a single read-only SQL SELECT (or WITH ... SELECT) against the shop database.\n"
    "Use for aggregations, filters, joins, and rankings (counts, revenue, top-N, date ranges).\n"
    "Do not use for INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or any DDL/DML — those are rejected.\n"
    "SQL must be one statement and must not contain comments (-- or /* */).\n"
    "Optional max_rows (default 100, min 1, max 500) caps how many rows are returned; if more rows exist, truncated=true.\n"
    "Results: columns, rows, row_count, truncated."
)


def list_tables() -> dict[str, Any]:
    path = get_db_path()
    with db.connect(path) as conn:
        return {"tables": db.list_user_tables(conn)}


def describe_table(table_name: str) -> dict[str, Any]:
    if not table_name or not str(table_name).strip():
        raise db.DatabaseError(
            "table_name is required and must be an existing user table. "
            "Call list_tables to see available tables."
        )
    path = get_db_path()
    with db.connect(path) as conn:
        return db.describe_table(conn, str(table_name).strip())


def run_select_query(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    if max_rows < MIN_MAX_ROWS or max_rows > MAX_MAX_ROWS:
        raise ValueError(
            f"max_rows must be between {MIN_MAX_ROWS} and {MAX_MAX_ROWS} (got {max_rows})."
        )
    try:
        safe_sql = validate_select(sql)
    except SqlGuardError:
        raise
    path = get_db_path()
    with db.connect(path) as conn:
        return db.run_select(conn, safe_sql, max_rows)
