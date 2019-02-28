"""
Represents a scheduled bot task.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from itertools import count
from time import sleep
from typing import Callable, DefaultDict, Dict, Iterable, List, NoReturn, Optional

from loguru import logger

from bestmobabot.api import API, AlreadyError, NotEnoughError, OutOfRetargetDelta, ResponseError
from bestmobabot.tracking import send_event


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


class Scheduler:
    def __init__(self, api: API):
        self.api = api
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task):
        if task.name in self.tasks:
            raise ValueError(f'task {task.name} is already added')
        self.tasks[task.name] = task

    def add_tasks(self, tasks: Iterable[Task]):
        for task in tasks:
            self.add_task(task)

    def run(self) -> NoReturn:
        logger.debug('Running scheduler.')
        retries: DefaultDict[datetime, List[Task]] = defaultdict(list)

        for at in iterate_seconds(now().replace(microsecond=0)):
            # Wait until the tick comes in the real world.
            while at > now():
                sleep(0.5)
            logger.trace('Tick: {:%b %d %H:%M:%S %Z}.', at)

            # Collect all tasks pending in the tick.
            pending = [task for task in self.tasks.values() if task.is_pending(at)] + retries.pop(int(at.timestamp()), [])

            # Execute the tasks.
            for task in pending:
                logger.info('Running {} scheduled at {:%b %d %H:%M:%S %Z}…', task.name, at)
                retry_at = self.execute(task)
                if retry_at:
                    logger.info('Task will be retried at {:%b %d %H:%M:%S %Z}.', retry_at)
                    retries[int(retry_at.timestamp())].append(task)  # TODO: persistence.

    def execute(self, task: Task) -> Optional[datetime]:
        send_event(category='bot', action=task.execute.__name__, user_id=self.api.user_id)
        self.api.last_responses.clear()
        try:
            next_run_at = task.execute()
        except TaskNotAvailable as e:
            logger.warning(f'Task unavailable: {e}.')
        except AlreadyError as e:
            logger.error(f'Already done: {e.description}.')
        except NotEnoughError as e:
            logger.error(f'Not enough: {e.description}.')
        except OutOfRetargetDelta:
            logger.error(f'Out of retarget delta.')
        except ResponseError as e:
            logger.opt(exception=e).error('API response error.')
        except Exception as e:
            logger.opt(exception=e).critical('Uncaught error.')
            for result in self.api.last_responses:
                logger.critical('API result: {}', result)
        else:
            logger.success('Well done.')
            return next_run_at


def now():
    return datetime.now(timezone.utc)


def iterate_seconds(since: datetime) -> Iterable[datetime]:
    for seconds in count():
        yield since + timedelta(seconds=seconds)
