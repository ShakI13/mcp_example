"""Configuration for the shop MCP server."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment() -> None:
    """Load `.env` from the process cwd if present.

    Existing process / Cursor ``mcp.json`` env vars take precedence
    (``load_dotenv`` does not override by default).
    """
    load_dotenv()


def get_db_path() -> Path | None:
    """Return resolved ``SHOP_DB_PATH``, or ``None`` if unset / blank."""
    raw = os.environ.get("SHOP_DB_PATH")
    if raw is None or not str(raw).strip():
        return None
    path = Path(str(raw).strip())
    if not path.is_absolute():
        path = Path.cwd() / path
    return path
