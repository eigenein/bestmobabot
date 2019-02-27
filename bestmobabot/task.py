"""
Represents a scheduled bot task.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Callable, Optional

NextRunAtCallable = Callable[[datetime], datetime]


@dataclass
class Task:
    next_run_at: NextRunAtCallable
    execute: Callable[[], Optional[datetime]]

    @staticmethod
    def at(*times_: time) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            upcoming = [
                since.astimezone(time_.tzinfo).replace(
                    hour=time_.hour,
                    minute=time_.minute,
                    second=time_.second,
                    microsecond=time_.microsecond,
                )
                for time_ in times_
            ]
            return min(
                upcoming_ if upcoming_ > since else upcoming_ + timedelta(days=1)
                for upcoming_ in upcoming
            )
        return next_run_at


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
