"""
Represents a scheduled bot task.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Callable, Iterable, Optional


@dataclass
class Task:
    at: Iterable[time]
    execute: Callable[[], Optional[datetime]]
    offset: timedelta = timedelta()

    @property
    def name(self) -> str:
        return self.execute.__name__

    def is_pending(self, at: datetime) -> bool:
        """
        Gets whether the task is pending at the time.
        """
        at = at + self.offset
        return any(at.astimezone(entry.tzinfo).time().replace(tzinfo=entry.tzinfo) == entry for entry in self.at)


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
