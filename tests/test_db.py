"""Tests for read-only database helpers."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from shop_mcp import db
from shop_mcp.config import get_db_path
from tests.fixtures import build_fixture_db


class TestDb(unittest.TestCase):
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

    def test_get_db_path_resolves(self) -> None:
        path = get_db_path()
        assert path is not None
        self.assertTrue(path.is_file())

    def test_list_user_tables(self) -> None:
        with db.connect(self.db_path) as conn:
            tables = db.list_user_tables(conn)
        names = {t["name"] for t in tables}
        self.assertEqual(names, {"customers", "products", "orders", "order_items"})
        self.assertTrue(all(t["type"] == "table" for t in tables))

    def test_describe_table(self) -> None:
        with db.connect(self.db_path) as conn:
            info = db.describe_table(conn, "customers")
        self.assertEqual(info["table_name"], "customers")
        cols = {c["name"]: c for c in info["columns"]}
        self.assertIn("id", cols)
        self.assertTrue(cols["id"]["primary_key"])
        # SQLite often reports INTEGER PRIMARY KEY with notnull=0 in PRAGMA table_info;
        # assert an explicit NOT NULL column instead.
        self.assertFalse(cols["name"]["nullable"])

    def test_missing_db_error(self) -> None:
        missing = Path(self._tmpdir.name) / "missing.db"
        with self.assertRaises(db.DatabaseError):
            with db.connect(missing):
                pass

    def test_row_limit_truncation(self) -> None:
        with db.connect(self.db_path) as conn:
            result = db.run_select(conn, "SELECT id FROM customers ORDER BY id", max_rows=2)
        self.assertEqual(result["row_count"], 2)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["columns"], ["id"])

    def test_row_limit_not_truncated(self) -> None:
        with db.connect(self.db_path) as conn:
            result = db.run_select(conn, "SELECT id FROM customers ORDER BY id", max_rows=100)
        self.assertEqual(result["row_count"], 3)
        self.assertFalse(result["truncated"])


if __name__ == "__main__":
    unittest.main()
