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
    def at(*times: time) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            upcoming = [
                since.astimezone(time_.tzinfo).replace(
                    hour=time_.hour,
                    minute=time_.minute,
                    second=time_.second,
                    microsecond=time_.microsecond,
                )
                for time_ in times
            ]
            return min(
                upcoming_ if upcoming_ > since else upcoming_ + timedelta(days=1)
                for upcoming_ in upcoming
            )
        return next_run_at

    @staticmethod
    def every_n_seconds(seconds: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            return since + timedelta(seconds=(seconds - (since.timestamp() - offset.total_seconds()) % seconds))
        return next_run_at

    @staticmethod
    def every_n_minutes(minutes: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_seconds(minutes * 60.0, offset)

    @staticmethod
    def every_n_hours(hours: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_minutes(hours * 60.0, offset)


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
