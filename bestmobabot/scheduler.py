from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, tzinfo
from typing import Any, Callable, List, MutableMapping

TIsPending = Callable[[datetime, datetime], bool]
TExecute = Callable[..., Any]


class Scheduler:
    def __init__(self, db: MutableMapping, prefix: str):
        self.db = db
        self.prefix = str
        self.tasks: List[Task] = []

    def between(self, earliest: time, latest: time) -> Task:
        if earliest.tzinfo:
            raise ValueError('offset-aware time is not allowed here')
        if latest.tzinfo:
            raise ValueError('offset-aware time is not allowed here')

        def _is_pending(last_executed_at: datetime, now: datetime) -> bool:
            return is_pending(last_executed_at, replace(now, earliest), replace(now, latest), now)
        return Task(self, _is_pending)

    def every(self, min_: timedelta, max_: timedelta) -> Task:
        def _is_pending(last_executed_at: datetime, now: datetime) -> bool:
            return is_pending(last_executed_at, last_executed_at + min_, last_executed_at + max_, now)
        return Task(self, _is_pending)

    def run_pending(self, tz: tzinfo):
        now = datetime.now().astimezone(tz)
        ...  # TODO


@dataclass
class Task:
    scheduler: Scheduler
    is_pending: TIsPending
    execute: TExecute = lambda: None

    def do(self, execute: TExecute):
        if execute.__name__ == (lambda: None).__name__:
            raise ValueError('lambda is not allowed here')
        self.execute = execute
        self.scheduler.tasks.append(self)


def is_pending(last_executed_at: datetime, earliest: datetime, latest: datetime, now: datetime) -> bool:
    # TODO: randomize time between earliest and latest, should be equally distributed.
    return last_executed_at < earliest <= now < latest


def replace(datetime_: datetime, time_: time) -> datetime:
    return datetime_.replace(
        hour=time_.hour,
        minute=time_.minute,
        second=time_.second,
        microsecond=time_.microsecond,
    )
