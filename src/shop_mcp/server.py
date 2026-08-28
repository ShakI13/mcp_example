"""MCP server entrypoints."""

from __future__ import annotations

import logging
import sys
from typing import Annotated, Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from shop_mcp import tools
from shop_mcp.config import load_environment
from shop_mcp.db import DatabaseError
from shop_mcp.sql_guard import SqlGuardError

logger = logging.getLogger("shop_mcp")

_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)


def create_server() -> MCPServer:
    """Build the configured MCP server (does not require the DB to exist)."""
    mcp = MCPServer(
        name="shop-mcp",
        instructions=(
            "Read-only shop analytics MCP. Discover tables with list_tables, "
            "inspect columns with describe_table, then run_select_query for SELECT/WITH."
        ),
    )

    @mcp.tool(
        name="list_tables",
        description=tools.LIST_TABLES_DESCRIPTION,
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    def list_tables() -> dict[str, Any]:
        try:
            return tools.list_tables()
        except (DatabaseError, SqlGuardError, ValueError) as exc:
            raise ToolError(str(exc)) from None

    @mcp.tool(
        name="describe_table",
        description=tools.DESCRIBE_TABLE_DESCRIPTION,
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    def describe_table(
        table_name: Annotated[
            str,
            Field(description="Name of an existing user table from list_tables."),
        ],
    ) -> dict[str, Any]:
        try:
            return tools.describe_table(table_name)
        except (DatabaseError, SqlGuardError, ValueError) as exc:
            raise ToolError(str(exc)) from None

    @mcp.tool(
        name="run_select_query",
        description=tools.RUN_SELECT_QUERY_DESCRIPTION,
        annotations=_READ_ONLY_ANNOTATIONS,
    )
    def run_select_query(
        sql: Annotated[
            str,
            Field(description="Single read-only SELECT or WITH ... SELECT statement."),
        ],
        max_rows: Annotated[
            int,
            Field(
                ge=tools.MIN_MAX_ROWS,
                le=tools.MAX_MAX_ROWS,
                description="Maximum rows to return (default 100, min 1, max 500).",
            ),
        ] = tools.DEFAULT_MAX_ROWS,
    ) -> dict[str, Any]:
        try:
            return tools.run_select_query(sql, max_rows=max_rows)
        except (DatabaseError, SqlGuardError, ValueError) as exc:
            raise ToolError(str(exc)) from None

    return mcp


def main() -> None:
    """Load config and run the stdio MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    load_environment()
    logger.info("Starting shop-mcp (stdio)")
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
