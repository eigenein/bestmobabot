"""
Database wrapper.
"""

import json
import sqlite3
from contextlib import AbstractContextManager, closing
from typing import Any, Iterable, Iterator, MutableMapping, Tuple, TypeVar

from loguru import logger

T = TypeVar('T')


class Database(AbstractContextManager, MutableMapping[str, Any]):
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, isolation_level=None)
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS `default` (
                    `key` TEXT PRIMARY KEY NOT NULL,
                    `value` TEXT,
                    `modified_on` DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def get_by_prefix(self, prefix: str) -> Iterable[Tuple[str, T]]:
        """
        Gets all values from the specified index.
        """
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute("SELECT `key`, `value` FROM `default` WHERE `key` LIKE ? || '%'", (prefix,))
            return ((key, json.loads(value)) for key, value in cursor.fetchall())

    def vacuum(self):
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('VACUUM')

    def __contains__(self, key: str) -> bool:
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT exists(SELECT 1 FROM `default` WHERE `key` = ?)', (key,))
            return bool(cursor.fetchone()[0])

    def __getitem__(self, key: str) -> Any:
        logger.trace('get {}', key)
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('SELECT value FROM `default` WHERE `key` = ?', (key,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(key)
            return json.loads(row[0])

    def __setitem__(self, key: str, value: Any) -> None:
        logger.trace('set {} = {!s:.40}…', key, value)
        with closing(self.connection.cursor()) as cursor:  # type: sqlite3.Cursor
            cursor.execute('''
                INSERT OR REPLACE INTO `default` (`key`, `value`)
                VALUES (?, ?)
            ''', (key, json.dumps(value)))

    def __len__(self) -> int:
        raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.__exit__(exc_type, exc_value, traceback)
