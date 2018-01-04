import heapq
from datetime import datetime, time
from time import sleep
from typing import Any, Callable, List, Tuple

from bestmobabot.api import Api, ApiError
from bestmobabot.responses import *
from bestmobabot.utils import logger

TAction = Callable[..., None]
TQueueItem = Tuple[datetime, int, TAction, Tuple]


class Bot:
    ONE_DAY = timedelta(days=1)

    EXPEDITION_COLLECT_REWARD = ExpeditionStatus(2)
    EXPEDITION_FINISHED = ExpeditionStatus(3)

    QUEST_STAMINA_MORNING = QuestId(10009)  # 8.00-11.00
    QUEST_STAMINA_AFTERNOON = QuestId(10010)  # 13.00-16.00
    QUEST_STAMINA_EVENING = QuestId(10015)  # 20.00-23.00

    QUEST_IN_PROGRESS = QuestState(1)
    QUEST_COLLECT_REWARD = QuestState(2)

    @staticmethod
    def start(api: Api) -> 'Bot':
        return Bot(api, api.get_user_info())

    def __init__(self, api: Api, user_info: UserInfo):
        self.api = api
        self.user_info = user_info
        self.queue: List[TQueueItem] = []
        self.action_counter = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.api.__exit__(exc_type, exc_val, exc_tb)

    def run(self):
        logger.info('🤖 Scheduling initial actions.')
        self.schedule(self.alarm_time(time(hour=9)), self.farm_daily_bonus)
        self.schedule(self.alarm_time(time(hour=22, minute=50)), self.farm_expeditions)
        self.schedule(self.alarm_time(time(hour=9)), self.farm_daily_quest, self.QUEST_STAMINA_MORNING)
        self.schedule(self.alarm_time(time(hour=14)), self.farm_daily_quest, self.QUEST_STAMINA_AFTERNOON)
        self.schedule(self.alarm_time(time(hour=21)), self.farm_daily_quest, self.QUEST_STAMINA_EVENING)

        logger.info('🤖 Running action queue.')
        while self.queue:
            when, _, action, args = heapq.heappop(self.queue)  # type: TQueueItem
            sleep_duration = (when - self.now()).total_seconds()
            if sleep_duration > 0.0:
                logger.info('💤 Next action %s%s at %s', action.__name__, args, when)
                sleep(sleep_duration)
            try:
                action(when, *args)
            except ApiError as e:
                if e.is_already():
                    logger.info('🤔 Already done.')
                elif e.is_invalid_session():
                    logger.warning('😱 Invalid session.')
                    # Re-authenticate.
                    self.api.authenticate()
                    # Re-schedule the action.
                    self.schedule(self.now(), action, *args)
                else:
                    logger.error('😱 API error.', exc_info=e)
            except Exception as e:
                logger.error('😱 Uncaught error.', exc_info=e)

        logger.fatal('🏳 Action queue is empty.')

    def now(self) -> datetime:
        return datetime.now(self.user_info.time_zone)

    def alarm_time(self, time_: time) -> datetime:
        now = datetime.now(self.user_info.time_zone).replace(microsecond=0)
        dt = now.replace(hour=time_.hour, minute=time_.minute, second=time_.second)
        return dt if dt > now else dt + timedelta(days=1)

    def schedule(self, when: datetime, action: TAction, *args: Any):
        self.action_counter += 1
        logger.debug('⏰ Schedule %s%s at %s', action.__name__, args, when)
        heapq.heappush(self.queue, (when, self.action_counter, action, args))

    def farm_daily_bonus(self, when: datetime):
        logger.info('💰 Farming daily bonus.')
        try:
            reward = self.api.farm_daily_bonus()
            logger.info('📈 Reward is %s.', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_daily_bonus)

    def farm_expeditions(self, when: datetime):
        logger.info('💰 Farming expeditions.')
        try:
            expeditions = self.api.list_expeditions()
            for expedition in expeditions.values():
                if expedition.status == self.EXPEDITION_COLLECT_REWARD:
                    reward = self.api.farm_expedition(expedition.id)
                    logger.info('📈 Reward is %s.', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_expeditions)

    def farm_daily_quest(self, when: datetime, quest_id: QuestId):
        logger.info('💰 Farming daily quest #%s.', quest_id)
        try:
            reward = self.api.farm_quest(quest_id)
            logger.info('📈 Reward is %s.', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_daily_quest, quest_id)

