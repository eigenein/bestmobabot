from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone, tzinfo
from typing import Any, Callable, List, MutableMapping

from loguru import logger

from bestmobabot.api import AlreadyError, NotEnoughError, OutOfRetargetDelta, ResponseError

TExecute = Callable[..., Any]


class Scheduler:
    def __init__(self, db: MutableMapping, prefix: str):
        self.db = db
        self.prefix = prefix
        self.tasks: List[Task] = []

    def set_defaults(self):
        last_executed_at = datetime.now(timezone.utc).timestamp()
        for task in self.tasks:
            self.db.setdefault(f'{self.prefix}:{task.name}:last_executed_at', last_executed_at)

    def add_task(self, task: Task) -> Scheduler:
        self.tasks.append(task)
        return self

    def run_pending(self, tz: tzinfo):
        now_ = datetime.now(tz)
        for task in self.tasks:
            # TODO: retries.
            last_executed_key = f'{self.prefix}:{task.name}:last_executed_at'
            last_executed_at = datetime.fromtimestamp(self.db[last_executed_key], timezone.utc)
            if not task.is_pending(last_executed_at, now_):
                logger.trace('{} is not pending.', task.name)
                continue
            logger.info('{} is pending.', task.name)
            self.db[last_executed_key] = now_.timestamp()
            try:
                task.execute()
            except AlreadyError as e:
                logger.error(f'Already done: {e.description}.')
            except NotEnoughError as e:
                logger.error(f'Not enough: {e.description}.')
            except OutOfRetargetDelta:
                logger.error('Out of retarget delta.')
            except ResponseError as e:
                logger.opt(exception=e).error('API response error.')
            else:
                logger.success('Well done.')


@dataclass
class Task:
    name: str
    execute: TExecute = lambda: None

    def is_pending(self, last_executed_at: datetime, now_: datetime) -> bool:
        logger.warning('Task {} is never executed.', self.name)
        return False


class EverydayTask(Task):
    earliest: time  # inclusive
    latest: time  # exclusive

    def is_pending(self, last_executed_at: datetime, now_: datetime) -> bool:
        # TODO: randomise between `earliest` and `latest`.
        return last_executed_at < now_ and self.earliest <= now_.time() < self.latest


class PeriodicTask(Task):
    min_: timedelta  # inclusive
    max_: timedelta  # exclusive

    def is_pending(self, last_executed_at: datetime, now_: datetime) -> bool:
        # TODO: randomise between `min_` and `max_`.
        return self.min_ <= now_ - last_executed_at
