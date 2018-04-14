"""
Database wrapper.
"""

import contextlib
import sqlite3


class Database(contextlib.AbstractContextManager):
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path)

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.__exit__(exc_type, exc_value, traceback)

    def ensure_table(self, table_name: str):
        ...
