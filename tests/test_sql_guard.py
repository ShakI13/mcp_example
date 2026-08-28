"""Tests for sql_guard.validate_select."""

from __future__ import annotations

import unittest

from shop_mcp.sql_guard import COMMENT_MESSAGE, REJECT_MESSAGE, SqlGuardError, validate_select


class TestSqlGuardAllows(unittest.TestCase):
    def test_simple_select(self) -> None:
        self.assertEqual(validate_select("SELECT 1"), "SELECT 1")

    def test_select_with_trailing_semicolon(self) -> None:
        self.assertEqual(validate_select("SELECT id FROM customers;"), "SELECT id FROM customers")

    def test_with_select(self) -> None:
        sql = "WITH c AS (SELECT id FROM customers) SELECT * FROM c"
        self.assertEqual(validate_select(sql), sql)

    def test_into_inside_identifier_not_blocked(self) -> None:
        sql = "SELECT into_col FROM products_into_stock"
        self.assertEqual(validate_select(sql), sql)


class TestSqlGuardRejects(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(SqlGuardError) as ctx:
            validate_select("   ")
        self.assertEqual(str(ctx.exception), REJECT_MESSAGE)

    def test_delete(self) -> None:
        with self.assertRaises(SqlGuardError) as ctx:
            validate_select("DELETE FROM customers")
        self.assertEqual(str(ctx.exception), REJECT_MESSAGE)

    def test_update(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("UPDATE customers SET name = 'x'")

    def test_drop(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("DROP TABLE customers")

    def test_insert(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("INSERT INTO customers (name) VALUES ('x')")

    def test_insert_into_form(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("INSERT INTO customers SELECT * FROM customers")

    def test_select_into_form(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("SELECT * INTO new_customers FROM customers")

    def test_multi_statement(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("SELECT 1; SELECT 2")

    def test_line_comment(self) -> None:
        with self.assertRaises(SqlGuardError) as ctx:
            validate_select("SELECT 1 -- comment")
        self.assertEqual(str(ctx.exception), COMMENT_MESSAGE)

    def test_block_comment(self) -> None:
        with self.assertRaises(SqlGuardError) as ctx:
            validate_select("SELECT 1 /* block */")
        self.assertEqual(str(ctx.exception), COMMENT_MESSAGE)

    def test_pragma(self) -> None:
        with self.assertRaises(SqlGuardError):
            validate_select("PRAGMA table_info(customers)")


if __name__ == "__main__":
    unittest.main()
