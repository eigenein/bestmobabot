from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, tzinfo
from typing import Any, Callable, List, MutableMapping

TIsPending = Callable[[datetime, datetime], bool]
TExecute = Callable[..., Any]


class Scheduler:
    def __init__(self, db: MutableMapping, prefix: str):
        self.db = db
        self.prefix = prefix
        self.tasks: List[Task] = []

    def add_task(self, name: str) -> Task:
        task = Task(name=name)
        self.tasks.append(task)
        return task

    def run_pending(self, tz: tzinfo):
        now = datetime.now().astimezone(tz)
        for task in self.tasks:
            last_executed_key = f'{self.prefix}:{task.name}:last_executed_at'
            try:
                last_executed_at = ...
            except KeyError:
                # It was never executed before. Initialise last execution time.
                self.db[last_executed_key] = now.timestamp()
                continue
            ...  # TODO


@dataclass
class Task:
    name: str
    is_pending: TIsPending = lambda: False
    execute: TExecute = lambda: None

    def between(self, earliest: time, latest: time) -> Task:
        if earliest.tzinfo:
            raise ValueError('offset-aware time is not allowed here')
        if latest.tzinfo:
            raise ValueError('offset-aware time is not allowed here')

        def _is_pending(last_executed_at: datetime, now: datetime) -> bool:
            # TODO: randomise between earliest and latest.
            return last_executed_at < replace(now, earliest) <= now < replace(now, latest)

        self.is_pending = _is_pending
        return self

    def every(self, min_: timedelta, max_: timedelta) -> Task:
        def _is_pending(last_executed_at: datetime, now: datetime) -> bool:
            # TODO: randomise between `last_executed_at + min_` and `last_executed_at + max_`.
            return last_executed_at < last_executed_at + min_ <= now

        self.is_pending = _is_pending
        return self

    def do(self, execute: TExecute):
        self.execute = execute


def replace(datetime_: datetime, time_: time) -> datetime:
    return datetime_.replace(
        hour=time_.hour,
        minute=time_.minute,
        second=time_.second,
        microsecond=time_.microsecond,
    )
