"""Tests for tool handler behavior."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from shop_mcp import tools
from shop_mcp.db import DatabaseError
from shop_mcp.sql_guard import SqlGuardError
from tests.fixtures import build_fixture_db


class TestTools(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = build_fixture_db(Path(self._tmpdir.name) / "fixture.db")
        self._old_env = os.environ.get("SHOP_DB_PATH")
        os.environ["SHOP_DB_PATH"] = str(self.db_path)

    def tearDown(self) -> None:
        if self._old_env is None:
            os.environ.pop("SHOP_DB_PATH", None)
        else:
            os.environ["SHOP_DB_PATH"] = self._old_env
        self._tmpdir.cleanup()

    def test_list_tables(self) -> None:
        result = tools.list_tables()
        names = [t["name"] for t in result["tables"]]
        self.assertEqual(names, ["customers", "order_items", "orders", "products"])

    def test_describe_table_unknown(self) -> None:
        with self.assertRaises(DatabaseError) as ctx:
            tools.describe_table("no_such_table")
        self.assertIn("not found", str(ctx.exception).lower())

    def test_run_select_query(self) -> None:
        result = tools.run_select_query(
            "SELECT country, COUNT(*) AS n FROM customers GROUP BY country ORDER BY n DESC"
        )
        self.assertIn("columns", result)
        self.assertGreaterEqual(result["row_count"], 1)
        self.assertFalse(result["truncated"])

    def test_row_limit_truncated_flag(self) -> None:
        result = tools.run_select_query("SELECT id FROM customers ORDER BY id", max_rows=1)
        self.assertEqual(result["row_count"], 1)
        self.assertTrue(result["truncated"])

    def test_mutation_rejected_and_db_unchanged(self) -> None:
        before = self._customer_count()
        with self.assertRaises(SqlGuardError):
            tools.run_select_query("DELETE FROM customers WHERE id = 1")
        self.assertEqual(self._customer_count(), before)

    def test_missing_db_on_tool_call(self) -> None:
        os.environ["SHOP_DB_PATH"] = str(Path(self._tmpdir.name) / "gone.db")
        with self.assertRaises(DatabaseError) as ctx:
            tools.list_tables()
        self.assertIn("SHOP_DB_PATH", str(ctx.exception))

    def _customer_count(self) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            return int(conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0])
        finally:
            conn.close()


class TestServerStartsWithoutDb(unittest.TestCase):
    def test_create_server_without_db(self) -> None:
        old = os.environ.pop("SHOP_DB_PATH", None)
        try:
            from shop_mcp.server import create_server

            server = create_server()
            self.assertEqual(server.name, "shop-mcp")
        finally:
            if old is not None:
                os.environ["SHOP_DB_PATH"] = old


if __name__ == "__main__":
    unittest.main()
