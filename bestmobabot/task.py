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

    def next_run_at(self, since: datetime) -> datetime:
        return min(self.yield_upcoming(since))

    def yield_upcoming(self, since: datetime) -> Iterable[datetime]:
        for time_ in self.at:
            upcoming = since.astimezone(time_.tzinfo).replace(
                hour=time_.hour,
                minute=time_.minute,
                second=time_.second,
                microsecond=time_.microsecond,
            )
            yield upcoming if upcoming > since else upcoming + timedelta(days=1)


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
