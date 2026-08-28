"""Server-side validation for read-only SELECT queries."""

from __future__ import annotations

import re

REJECT_MESSAGE = (
    "Rejected: only read-only SELECT queries are allowed. "
    "Destructive or DDL operations are not permitted."
)

COMMENT_MESSAGE = (
    "Rejected: SQL comments are not allowed. "
    "Resubmit without -- or /* */ comments."
)

_DANGEROUS_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "REPLACE",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "REINDEX",
    "VACUUM",
    "GRANT",
    "REVOKE",
    "PRAGMA",
    "EXEC",
    "EXECUTE",
)

_DANGEROUS_RE = re.compile(
    r"\b(?:" + "|".join(_DANGEROUS_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

_SELECT_INTO_RE = re.compile(r"\bSELECT\b[\s\S]*\bINTO\b", re.IGNORECASE)


class SqlGuardError(ValueError):
    """Raised when SQL fails read-only validation."""


def _strip_string_literals(sql: str) -> str:
    """Replace quoted string contents so keyword checks ignore literals."""

    def repl(match: re.Match[str]) -> str:
        return "''"

    # Single-quoted SQL strings ('' escape) and double-quoted identifiers.
    return re.sub(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"", repl, sql)


def validate_select(sql: str) -> str:
    """Validate ``sql`` as a single read-only SELECT / WITH…SELECT.

    Returns the statement with a trailing semicolon removed (if any).
    Raises ``SqlGuardError`` on rejection.
    """
    if sql is None or not str(sql).strip():
        raise SqlGuardError(REJECT_MESSAGE)

    raw = str(sql)
    if "--" in raw or "/*" in raw or "*/" in raw:
        raise SqlGuardError(COMMENT_MESSAGE)

    stripped = raw.strip()
    body = stripped.rstrip(";").strip()
    if not body:
        raise SqlGuardError(REJECT_MESSAGE)
    if ";" in body:
        raise SqlGuardError(REJECT_MESSAGE)

    head = body.lstrip()
    upper_head = head[:6].upper()
    if not (upper_head.startswith("SELECT") or upper_head.startswith("WITH")):
        raise SqlGuardError(REJECT_MESSAGE)

    # WITH must eventually be a SELECT CTE statement (not WITH-less DDL).
    if head.upper().startswith("WITH") and not re.search(
        r"\bSELECT\b", body, re.IGNORECASE
    ):
        raise SqlGuardError(REJECT_MESSAGE)

    scrubbed = _strip_string_literals(body)
    if _DANGEROUS_RE.search(scrubbed):
        raise SqlGuardError(REJECT_MESSAGE)
    if _SELECT_INTO_RE.search(scrubbed):
        raise SqlGuardError(REJECT_MESSAGE)

    return body
