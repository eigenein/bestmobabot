"""
Database wrapper.
"""

import sqlite3
from contextlib import AbstractContextManager, closing
from typing import Callable, Iterable, Optional, Tuple, TypeVar

import ujson as json

T = TypeVar('T')


# noinspection SqlResolve
class Database(AbstractContextManager):
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, isolation_level=None)
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "default" (
                    "key" TEXT PRIMARY KEY NOT NULL,
                    value TEXT,
                    modified_on DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def exists(self, key: str) -> bool:
        """
        Tests whether the specified key exists.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT exists(SELECT 1 FROM "default" WHERE "key" = ?)', (key,))
            return bool(cursor.fetchone()[0])

    def get_by_key(self, key: str, default: Optional[T] = None, loads: Callable[[str], T] = json.loads) -> Optional[T]:
        """
        Gets single value by the specified index and key.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT value FROM "default" WHERE "key" = ?', (key,))
            row = cursor.fetchone()
            return loads(row[0]) if row else default

    def get_by_prefix(self, prefix: str, loads: Callable[[str], T] = json.loads) -> Iterable[Tuple[str, T]]:
        """
        Gets all values from the specified index.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT "key", value FROM "default" WHERE "key" LIKE ? || "%"', (prefix,))
            return ((key, loads(value)) for key, value in cursor.fetchall())

    def set(self, key: str, value: T, *, dumps: Callable[[T], str] = json.dumps):
        """
        Inserts or updates value on the specified index and key.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                INSERT OR REPLACE INTO "default" ("key", "value")
                VALUES (?, ?)
            ''', (key, dumps(value)))

    def vacuum(self):
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('VACUUM')

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.__exit__(exc_type, exc_value, traceback)
