"""
Database wrapper.
"""

import contextlib
import json
import sqlite3
from typing import Callable, Optional, TypeVar

T = TypeVar('T')


class Database(contextlib.AbstractContextManager):
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.__exit__(exc_type, exc_value, traceback)

    def ensure_table(self, table_name: str):
        with self.connection.cursor() as cursor:  # type: sqlite3.Cursor
            cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" (key TEXT PRIMARY KEY, value TEXT)')

    def get(self, table_name: str, key: str, loads: Callable[[str], T] = json.loads) -> Optional[T]:
        self.ensure_table(table_name)
        with self.connection.cursor() as cursor:  # type: sqlite3.Cursor
            cursor.execute(f'SELECT value FROM "{table_name}" WHERE key = %s', (key,))
            row = cursor.fetchone()
            return loads(row[0]) if row else None
