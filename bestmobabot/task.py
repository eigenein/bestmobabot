"""
Represents a scheduled bot task.
"""

from datetime import datetime, timedelta, tzinfo
from typing import Callable, NamedTuple, Optional, Tuple


NextRunAtCallable = Callable[[datetime], datetime]


class Task(NamedTuple):
    next_run_at: NextRunAtCallable
    execute: Callable[..., Optional[datetime]]
    args: Tuple = ()

    def __str__(self):
        return f'{self.execute.__name__}{self.args}'

    @staticmethod
    def at(*, hour: int, minute: int, tz: Optional[tzinfo] = None) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            since = since.astimezone(tz)
            upcoming = since.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return upcoming if upcoming > since else upcoming + timedelta(days=1)
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

    @staticmethod
    def asap() -> NextRunAtCallable:
        """
        Executes task as soon as possible. Only used for development.
        """
        def next_run_at(since: datetime) -> datetime:
            return since
        return next_run_at


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """
