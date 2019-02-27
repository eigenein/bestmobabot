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

    def next_runs(self, since: datetime) -> Iterable[datetime]:
        # TODO: unit tests.
        for time_ in self.at:
            upcoming = since.astimezone(time_.tzinfo).replace(
                hour=time_.hour,
                minute=time_.minute,
                second=time_.second,
                microsecond=time_.microsecond,
            ) + self.offset
            yield upcoming if upcoming > since else upcoming + timedelta(days=1)


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
