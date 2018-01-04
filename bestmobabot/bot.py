import heapq
import time
from datetime import datetime, timedelta
from typing import Callable, List, Tuple, Union

from bestmobabot.api import Api
from bestmobabot.utils import logger

TAction = Callable[[], None]
TQueueItem = Tuple[datetime, TAction]


class Bot:
    def __init__(self, api: Api):
        self.api = api
        self.queue: List[TQueueItem] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.api.__exit__(exc_type, exc_val, exc_tb)

    def run(self):
        logger.info('🤖 Scheduling initial actions.')
        self.schedule_farm_expeditions()

        logger.info('🤖 Running action queue.')
        while self.queue:
            when, action = heapq.heappop(self.queue)  # type: TQueueItem
            sleep_duration = (when - datetime.now()).total_seconds()
            if sleep_duration > 0.0:
                logger.info('💤 Next action %s at %s', action.__name__, when)
                time.sleep(sleep_duration)
            action()

        logger.fatal('🏳 Action queue is empty.')

    def schedule(self, when: Union[datetime, timedelta], action: TAction):
        if isinstance(when, timedelta):
            when = datetime.now() + when
        when = when.replace(microsecond=0)
        logger.debug('⏰ Schedule %s at %s', action.__name__, when)
        heapq.heappush(self.queue, (when, action))

    def schedule_farm_expeditions(self):
        self.schedule(timedelta(hours=12), self.farm_expeditions)

    def farm_expeditions(self):
        logger.info('💰 Farming expeditions.')
        # TODO
        self.schedule_farm_expeditions()

