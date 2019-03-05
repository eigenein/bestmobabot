from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from itertools import count
from time import sleep
from typing import Callable, DefaultDict, Dict, Iterable, List, NoReturn, Optional

from loguru import logger

import bestmobabot.bot
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
        return any(
            at.astimezone(entry.tzinfo).time().replace(tzinfo=entry.tzinfo) == entry.replace(microsecond=0)
            for entry in self.at
        )


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """


class Scheduler:
    def __init__(self, bot: bestmobabot.bot.Bot):
        self.bot = bot
        self.db = bot.db
        self.tasks: Dict[str, Task] = {}
        self.retries: DefaultDict[int, List[str]] = defaultdict(list)

    @property
    def user_name(self) -> str:
        return self.bot.user.name

    def add_task(self, task: Task):
        if task.name in self.tasks:
            raise ValueError(f'task {task.name} is already added')
        self.tasks[task.name] = task

    def add_tasks(self, tasks: Iterable[Task]):
        for task in tasks:
            self.add_task(task)

    def run(self) -> NoReturn:
        logger.info('Running scheduler.')

        # Restore retries, dropping expired ones.
        now_ = now().timestamp()
        self.retries.update(
            (timestamp, name)
            for timestamp, name in self.db.get(f'{self.bot.user.id}:retries', [])
            if timestamp > now_
        )
        logger.debug('{} retries retrieved.', len(self.retries))

        # Main task loop, never ending.
        for at in iterate_seconds(now(self.bot.user.tz).replace(microsecond=0)):
            # Wait until the tick comes in the real world.
            while at > now():
                sleep(0.5)
            logger.trace('Tick: {:%b %d %H:%M:%S %Z}.', at)

            # Collect all tasks pending in the tick.
            pending = [task for task in self.tasks.values() if task.is_pending(at)]
            pending.extend(self.tasks[name] for name in self.retries.pop(int(at.timestamp()), []))

            # Execute the tasks.
            for task in pending:
                logger.info('Running {} scheduled at {:%b %d %H:%M:%S %Z}…', task.name, at)
                retry_at = self.execute(task)
                if retry_at:
                    retry_at = retry_at.astimezone(self.bot.user.tz)
                    logger.info('{} will be retried at {:%b %d %H:%M:%S %Z}.', task.name, retry_at)
                    self.retries[int(retry_at.timestamp())].append(task.name)
                    self.bot.notifier.reset().notify(
                        f'⏰ *{self.user_name}* попробует снова в *{retry_at:%b %d %H:%M:%S %Z}*.')

            # Store the retries if something was executed.
            if pending:
                self.db[f'{self.bot.user.id}:retries'] = list(self.retries.items())

    def execute(self, task: Task) -> Optional[datetime]:
        send_event(category='bot', action=task.execute.__name__, user_id=self.bot.user.id)
        self.bot.api.last_responses.clear()
        self.bot.notifier.reset()
        try:
            next_run_at = task.execute()
        except TaskNotAvailable as e:
            logger.warning(f'Task unavailable: {e}.')
            self.bot.notifier.notify(f'Задача `{task.name}` недоступна в боте *{self.user_name}*.')
        except Exception as e:
            self.bot.notifier.notify(
                f'‼️ Бот *{self.user_name}* совершил ошибку.'
                f' *[Papertrail](https://papertrailapp.com/events?time={int(now().timestamp())})*'
            )
            logger.opt(exception=e).critical('Uncaught error.')
            for result in self.bot.api.last_responses:
                logger.critical('API response: {}', result)
        else:
            logger.success('Well done.')
            return next_run_at


def now(tz=timezone.utc):
    return datetime.now(tz)


def iterate_seconds(since: datetime) -> Iterable[datetime]:
    for seconds in count():
        yield since + timedelta(seconds=seconds)
