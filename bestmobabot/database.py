"""
Database wrapper.
"""

import json
import sqlite3
from contextlib import AbstractContextManager, closing
from typing import Callable, Iterable, Optional, Tuple, TypeVar

T = TypeVar('T')


# noinspection SqlResolve
class Database(AbstractContextManager):
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "default"
                ("index" TEXT, "key" TEXT, value TEXT, PRIMARY KEY ("index", "key"))
            ''')

    def exists(self, index: str, key: str) -> bool:
        """
        Tests whether the specified key exists.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT exists(SELECT 1 FROM "default" WHERE "index" = ? AND "key" = ?)', (index, key))
            return bool(cursor.fetchone()[0])

    def get_by_key(self, index: str, key: str, *, default: Optional[T] = None, loads: Callable[[str], T] = json.loads) -> Optional[T]:
        """
        Gets single value by the specified index and key.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT value FROM "default" WHERE "index" = ? AND "key" = ?', (index, key,))
            row = cursor.fetchone()
            return loads(row[0]) if row else default

    def get_by_index(self, index: str, *, loads: Callable[[str], T] = json.loads) -> Iterable[Tuple[str, T]]:
        """
        Gets all values from the specified index.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT "key", value FROM "default" where "index" = ?', (index,))
            return ((key, loads(value)) for key, value in cursor.fetchall())

    def set(self, index: str, key: str, value: T, *, dumps: Callable[[T], str] = json.dumps):
        """
        Inserts or updates value on the specified index and key.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                INSERT OR REPLACE INTO "default" ("index", "key", "value")
                VALUES (?, ?, ?)
            ''', (index, key, dumps(value)))

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.__exit__(exc_type, exc_value, traceback)
