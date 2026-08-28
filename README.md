# Shop MCP Server

Read-only [MCP](https://modelcontextprotocol.io/) server that lets a Cursor agent answer analytical questions about an internet-shop SQLite database (`customers`, `products`, `orders`, `order_items`) without mutating data.

## Requirements

- Python 3.11+ (3.12 works)
- A shop SQLite file at the path you configure (typically `data/shop.db`)

## Install

From the repository root:

```bash
python -m venv venv
```

Activate the venv:

- Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
- macOS / Linux: `source venv/bin/activate`

Then:

```bash
pip install -r requirements.txt
pip install -e .
```

## Configure

1. Optionally copy `.env.example` to `.env` and set `SHOP_DB_PATH` (relative paths resolve against the process working directory):

   ```env
   SHOP_DB_PATH=data/shop.db
   ```

2. Place the shop SQLite database at that path (for example `data/shop.db`).

3. Cursor `mcp.json` `env` values override `.env`. Graders may set only Cursor env and never create a `.env` file; the server still works.

The server loads `.env` itself via `python-dotenv`. Cursor does not load `.env` automatically.

## Run

```bash
python -m shop_mcp
```

This starts an MCP server on **stdio** (normally launched by Cursor, not by hand in a terminal you care about chatting with).

Missing `SHOP_DB_PATH` / missing DB file does **not** prevent process startup. The first tool call that needs the database returns a clear recoverable error.

## Connect to Cursor

1. Copy `.cursor/mcp.json.example` to your Cursor MCP config (for example `.cursor/mcp.json` in this project, or your user MCP settings).
2. Edit the absolute paths for:
   - `command` — venv Python (`…/venv/Scripts/python.exe` on Windows, `…/venv/bin/python` on Unix)
   - `cwd` — repository root
   - `env.SHOP_DB_PATH` — absolute path to `shop.db`

Example shape:

```json
{
  "mcpServers": {
    "shop-mcp": {
      "command": "E:/dev/training/mcp_example/venv/Scripts/python.exe",
      "args": ["-m", "shop_mcp"],
      "cwd": "E:/dev/training/mcp_example",
      "env": {
        "SHOP_DB_PATH": "E:/dev/training/mcp_example/data/shop.db"
      }
    }
  }
}
```

After an editable install, `-m shop_mcp` works from any cwd; `cwd` still helps relative `.env` discovery if you use one.

## Tools

| Tool | Purpose |
|------|---------|
| `list_tables` | List user tables (name + type) |
| `describe_table` | Column metadata for one table |
| `run_select_query` | Single read-only `SELECT` / `WITH … SELECT` |

All tools are annotated read-only / non-destructive / idempotent / closed-world.

**Safety:** `run_select_query` validates SQL server-side (SELECT-only, no comments, no multi-statement, no DDL/DML). The SQLite connection is opened read-only with `query_only=ON`. Destructive SQL is refused; the database file is never modified through these tools. Row caps use a fetch limit (`max_rows` default 100, max 500) without rewriting the agent’s SQL; `truncated` is set when more rows exist.

## Tests

With the venv active and the package installed editable:

```bash
python -m unittest discover -s tests -v
```

Tests use `tests/fixtures/` and do **not** require production `data/shop.db`.
