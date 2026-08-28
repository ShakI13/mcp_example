# Shop MCP Server — Implementation Spec (v1)

Status: **approved for implementation**  
Language: Python 3.11  
Package / module name: `shop_mcp`  
Transport: stdio  
DB: SQLite `shop.db` (read-only; file uploaded later)

---

## 1. Goal

Build an MCP server that lets a Cursor AI agent answer analytical questions about an internet-shop SQLite database (`customers`, `products`, `orders`, `order_items`) without mutating data.

Grading is agent-facing: tools must start, be discoverable, support multi-step queries, and refuse destructive operations.

---

## 2. Decisions (locked)

| Topic | Choice |
|-------|--------|
| Tool design | **Hybrid**: schema tools + one guarded SELECT |
| Scope v1 | Core homework only (no Docker, no pagination extras, no specialized analytics tools) |
| README | English |
| Agent config | Cursor (`.cursor/mcp.json.example`) for now |
| Env | `.env` / `.env.example`; no absolute paths in source |
| Install | Editable install via `pyproject.toml` (`pip install -e .`) so `python -m shop_mcp` works |
| Tests | `unittest` (helpers + behavior; no full MCP Inspector E2E required) |
| Layout | `src/`, `tests/`, `docs/`, `data/` |
| Venv | `./venv`, Python 3.11 |

### Design note (cheat sheet vs homework)

The MCP cheat sheet marks unrestricted `run_sql` as a critical anti-pattern. This homework explicitly allows a generic query tool **or** specialized tools. v1 accepts a **constrained** `run_select_query` (SELECT-only validation + read-only SQLite) as an agent-facing escape hatch for Tasks 2–8, instead of pure semantic analytics tools. Safety is enforced server-side, never by trusting the model.

---

## 3. Out of scope (v1)

- Pagination beyond a hard max row limit / `truncated` flag
- Specialized analytics tools (`get_top_products`, etc.)
- Docker
- Claude Desktop / other host configs
- Resources / prompts primitives (tools only)
- Write paths, migrations, admin tools
- End-to-end tests through a live MCP client/Inspector (optional later)
- Relying on `PYTHONPATH=src` without installing the package

Bonus items may be added in a later revision of this spec.

---

## 4. Repository layout

```text
mcp_example/
├── .cursor/
│   └── mcp.json.example
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml            # package metadata; enables pip install -e .
├── requirements.txt          # runtime pins (mcp, python-dotenv); used by README
├── data/
│   └── shop.db               # provided later; not required to write code
├── docs/
│   ├── MCP_Cheat_Sheet_2026.md
│   └── shop_mcp_spec.md      # this file
├── src/
│   └── shop_mcp/
│       ├── __init__.py
│       ├── __main__.py       # python -m shop_mcp
│       ├── config.py
│       ├── db.py
│       ├── sql_guard.py
│       ├── server.py
│       └── tools.py
├── tests/
│   ├── __init__.py
│   ├── fixtures/             # tiny SQLite or SQL bootstrap for tests
│   ├── test_sql_guard.py
│   ├── test_db.py
│   └── test_tools.py
└── venv/                     # local; gitignored
```

### Install contract (locked)

From repo root, with venv active:

```bash
pip install -r requirements.txt
pip install -e .
```

`pyproject.toml` must declare package discovery under `src/shop_mcp` so `python -m shop_mcp` resolves without setting `PYTHONPATH`.

### Cursor config example

```json
{
  "mcpServers": {
    "shop-mcp": {
      "command": "/absolute/path/to/repo/venv/Scripts/python.exe",
      "args": ["-m", "shop_mcp"],
      "cwd": "/absolute/path/to/repo",
      "env": {
        "SHOP_DB_PATH": "/absolute/path/to/repo/data/shop.db"
      }
    }
  }
}
```

Paths are host-local. README documents copying `.cursor/mcp.json.example` and adjusting them. After editable install, the venv interpreter can run `-m shop_mcp` from any cwd; `cwd` still helps relative `.env` discovery if used.

---

## 5. Dependencies

| Package | Purpose |
|---------|---------|
| `mcp[cli]` | Official MCP Python SDK v2 — stdio server, tool registration |
| `python-dotenv` | Load `.env` inside the server process |

Stdlib only otherwise: `sqlite3`, `os`, `pathlib`, `re`, `logging`.

`requirements.txt` pins reasonably current compatible versions at implement time. `pyproject.toml` lists the same runtime deps for editable install.

---

## 6. Configuration

### Environment

| Variable | Required | Meaning |
|----------|----------|---------|
| `SHOP_DB_PATH` | Yes (for successful queries) | Path to SQLite file (absolute, or relative to process `cwd`) |

`.env.example`:

```env
SHOP_DB_PATH=data/shop.db
```

Rules:

- Never hardcode machine-absolute paths in Python sources.
- Load `.env` from process `cwd` (and optionally project root if clearly defined) if the file exists.
- **Precedence:** process / Cursor `mcp.json` `env` **overrides** values from `.env`. Graders may set only `mcp.json` `env` and never create a `.env` file; the server must still work.
- Cursor does not automatically load `.env`; the server must call `load_dotenv` itself.
- Missing / unreadable DB: **do not fail process startup** (MCP stdio handshake must succeed). Fail on **first tool call** that needs the DB, with a clear recoverable message (see §10).

---

## 7. MCP tools (v1)

All tools: `readOnlyHint=true`, `destructiveHint=false`, `idempotentHint=true`, `openWorldHint=false` (or SDK equivalents).

Canonical tool description strings: **Appendix A**.

### 7.1 `list_tables`

**When to use:** Discover what tables exist; Task 1.

**Params:** none.

**Returns (locked shape):**

```json
{
  "tables": [
    { "name": "customers", "type": "table" },
    { "name": "orders", "type": "table" }
  ]
}
```

- Include user tables only (exclude `sqlite_*` internals).
- Do **not** invent business “purpose” hints; the agent uses `describe_table` + its own reasoning for Task 1 explanations.

**Errors:** DB unavailable → recoverable message (§10).

### 7.2 `describe_table`

**When to use:** Understand columns/types before writing SQL; Task 1.

**Params:**

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `table_name` | string | yes | Must be an existing user table |

**Returns (locked shape):**

```json
{
  "table_name": "customers",
  "columns": [
    {
      "name": "id",
      "type": "INTEGER",
      "nullable": false,
      "primary_key": true
    }
  ]
}
```

Use server-side `PRAGMA table_info` (allowed only in `db.py` / tool implementation — **not** via `run_select_query`).

**Errors:** unknown table → clear not-found message (do not list every table unless helpful in one short hint).

### 7.3 `run_select_query`

**When to use:** Analytical / multi-table questions (Tasks 2–8). Agent supplies SQL.

**Params:**

| Name | Type | Required | Schema constraints | Notes |
|------|------|----------|--------------------|-------|
| `sql` | string | yes | non-empty | Single read-only `SELECT` or `WITH … SELECT` |
| `max_rows` | integer | no | **minimum 1, maximum 500**, default **100** | Encode min/max/default in the tool JSON Schema, not only in prose |

**Returns (locked shape):**

```json
{
  "columns": ["col1", "col2"],
  "rows": [["a", 1], ["b", 2]],
  "row_count": 2,
  "truncated": false
}
```

- `row_count` = number of rows **returned** (after cap).
- `truncated` = `true` if more rows were available than returned.

**Server behavior (locked):**

1. Validate with `sql_guard` (§8).
2. Execute via read-only connection (§9).
3. **Row limit via Python fetch cap only** — e.g. `fetchmany(max_rows + 1)` (or equivalent). If more than `max_rows` rows are available, return the first `max_rows` and set `truncated: true`. **Do not rewrite or append `LIMIT` to the agent’s SQL.**
4. Never return Python stack traces in the tool result.

---

## 8. SQL safety (`sql_guard.py`)

### Allow

- Exactly one statement (no second statement after `;`).
- Statement root: `SELECT …` or `WITH … SELECT …` (read-only CTEs).

### Comment handling (locked)

**Reject** if the SQL contains SQL comments:

- line comments: `--`
- block comments: `/* … */`

Do not strip-and-continue. Message should tell the agent to resubmit without comments.

### Deny before execute

Reject (case-insensitive) when the statement is not a pure read `SELECT` / `WITH…SELECT`, including presence of dangerous **statement forms** / keywords, for example:

- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `TRUNCATE`
- `ATTACH`, `DETACH`, `REINDEX`, `VACUUM`
- `GRANT`, `REVOKE`
- `PRAGMA`, `EXEC`, `EXECUTE`
- Multi-statement input
- Empty / whitespace-only SQL
- Non-SELECT roots after normalization

**`INTO` rule (locked):** do **not** ban the substring/word `INTO` globally (false positives on identifiers). Instead reject explicit forms such as:

- `INSERT INTO`
- `REPLACE INTO`
- `SELECT … INTO` (if matched as a statement shape)

### Error shape for agent

```text
Rejected: only read-only SELECT queries are allowed. Destructive or DDL operations are not permitted.
```

For comments specifically, a distinct short message is allowed, e.g. comments are not allowed — resubmit without `--` or `/* */`.

No partial execution.

---

## 9. Database access (`db.py`)

- Open with SQLite **read-only** URI, e.g. `file:<path>?mode=ro`.
- Also set `PRAGMA query_only=ON` on the connection (server-side defense in depth).
- Connection lifecycle: short-lived context manager per tool call; close cleanly.
- Path resolution: from `SHOP_DB_PATH` via `config.py` (absolute as-is; relative resolved against process `cwd`).

Tests use `tests/fixtures/` (prebuilt tiny DB or SQL bootstrap in `setUp`). Production `data/shop.db` is not required to run tests.

---

## 10. Errors & logging

| Case | Behavior |
|------|----------|
| Process start, DB missing | **Still start** MCP stdio server successfully |
| Tool call, DB missing/unreadable | Tool error: set `SHOP_DB_PATH` / place file at that path |
| SQL rejected by guard | Explicit refusal (safety requirement) |
| SQL comments present | Explicit refusal; ask to retry without comments |
| SQLite operational/syntax error | Short message; no traceback in tool output |
| Unknown table in `describe_table` | Not-found message |
| `max_rows` out of schema range | Schema/validation error from SDK or clear message |

Logging: **stderr only** (stdio stdout is the MCP protocol stream).

---

## 11. Homework coverage mapping

| Task | How the agent should succeed |
|------|------------------------------|
| 1 Tables + meaning | `list_tables` + `describe_table` (+ agent explains) |
| 2 Germany customers | `run_select_query` + `COUNT` / filter |
| 3 Country most customers | `GROUP BY` country + `ORDER BY` + `LIMIT` |
| 4 Top spender | Join orders/items/products (or order totals) → customer name, email, sum |
| 5 Top 5 products | Aggregate units + revenue |
| 6 Top 3 categories by revenue | orders → order_items → products |
| 7 Revenue in 2025 | Filter order dates in 2025 |
| 8 Most orders by customer | `COUNT` orders per customer |
| Safety: delete cancelled | Guard rejects; DB unchanged |

Exact column names come from the real `shop.db` when uploaded. Tools must not hardcode business column names; the agent discovers them via `describe_table`.

---

## 12. Tests (`unittest`)

Minimum for v1:

1. **Guard allows** simple `SELECT` and `WITH … SELECT`.
2. **Guard rejects** `DELETE`, `UPDATE`, `DROP`, `INSERT`, `INSERT INTO`, multi-statement, empty, and SQL containing `--` or `/* */` comments.
3. **Guard does not false-positive** on benign identifiers that merely contain letters like “into” inside a name **unless** a banned statement form is present (add at least one negative test for over-blocking if practical).
4. **Row limit / truncated flag** via fetch-cap behavior (in-memory or fixture DB).
5. **`describe_table`** unknown table error.
6. **Read-only**: mutation attempt via tool/guard path does not change fixture DB (row counts or equivalent before/after).

**Out of scope for v1 tests:** spinning up a full MCP client session / Inspector E2E. Prefer unit tests of `sql_guard`, `db`, and tool handler functions.

Tests must pass without production `data/shop.db`.

Run:

```bash
# from repo root, venv active, package installed editable
python -m unittest discover -s tests -v
```

---

## 13. README contents (required)

English sections:

1. What this is  
2. Requirements (Python 3.11)  
3. Install (`python -m venv venv`, activate, `pip install -r requirements.txt`, `pip install -e .`)  
4. Configure (optional `.env` from `.env.example`; place `data/shop.db`; note Cursor `env` overrides)  
5. Run (`python -m shop_mcp` — stdio; normally launched by Cursor)  
6. Connect to Cursor (copy/adapt `.cursor/mcp.json.example`; absolute paths)  
7. Tools overview + safety note  
8. Tests  

---

## 14. Implementation order

1. Scaffold dirs, `pyproject.toml`, `requirements.txt`, `.env.example`, package skeleton  
2. `config.py` + `db.py` + `sql_guard.py`  
3. Tools + `server.py` / `__main__.py` (descriptions from Appendix A)  
4. Fixture DB + unittest  
5. README + `.cursor/mcp.json.example`  
6. After `shop.db` upload: smoke-check Tasks 1–8 via Cursor agent  

---

## 15. Acceptance criteria (v1)

- [ ] Editable install works; `python -m shop_mcp` starts as stdio MCP using the official SDK  
- [ ] Missing DB does not prevent process start; first DB-backed tool call returns a clear error  
- [ ] Cursor config example works after local path edit  
- [ ] Agent sees three tools with Appendix A–quality descriptions and schema bounds on `max_rows`  
- [ ] Agent can answer Tasks 1–8 once `shop.db` is present  
- [ ] Destructive SQL and commented SQL are refused; DB file unchanged  
- [ ] Row limits enforced by fetch cap; `truncated` set correctly; agent SQL not rewritten  
- [ ] No absolute paths baked into source  
- [ ] `unittest` suite passes without production DB (fixture)  
- [ ] README covers install → configure → run → connect  

---

## 16. Open item (non-blocking)

- **Deliver `data/shop.db`** (or SQL dump to generate it) before final agent verification of Tasks 2–8.

---

## Appendix A — Tool description strings (locked)

Use these (or substantially identical) texts in the MCP tool definitions.

### `list_tables`

```text
List user tables in the shop SQLite database (name and type only).
Use this first when you need to know what data exists.
For column details, call describe_table next.
Read-only: never modifies the database.
```

### `describe_table`

```text
Describe columns for one table (name, SQL type, nullable, primary_key).
Use after list_tables before writing SQL for run_select_query.
Parameter table_name must be an existing user table.
Read-only: never modifies the database.
```

### `run_select_query`

```text
Run a single read-only SQL SELECT (or WITH ... SELECT) against the shop database.
Use for aggregations, filters, joins, and rankings (counts, revenue, top-N, date ranges).
Do not use for INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, or any DDL/DML — those are rejected.
SQL must be one statement and must not contain comments (-- or /* */).
Optional max_rows (default 100, min 1, max 500) caps how many rows are returned; if more rows exist, truncated=true.
Results: columns, rows, row_count, truncated.
```
