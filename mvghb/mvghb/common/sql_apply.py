"""Apply a multi-statement SQL file via a psycopg connection.

Strips `--` line comments before splitting on `;` so that semicolons
inside comments don't split mid-comment.
"""
from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import text


_LINE_COMMENT = re.compile(r"--[^\n]*")


def _strip_line_comments(sql: str) -> str:
    return _LINE_COMMENT.sub("", sql)


def split_statements(sql: str) -> list[str]:
    cleaned = _strip_line_comments(sql)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def apply_sql_file(s: Session, path: Path) -> int:
    sql = path.read_text()
    n = 0
    for stmt in split_statements(sql):
        s.execute(text(stmt))
        n += 1
    return n
