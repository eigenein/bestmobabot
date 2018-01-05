import heapq
from datetime import datetime, time
from time import sleep
from typing import Any, Callable, List, Tuple

from bestmobabot.api import AlreadyError, Api, InvalidResponseError, InvalidSessionError
from bestmobabot.responses import *
from bestmobabot.utils import logger

TAction = Callable[..., None]
TQueueItem = Tuple[datetime, int, TAction, Tuple]


class Bot:
    ONE_DAY = timedelta(days=1)

    EXPEDITION_COLLECT_REWARD = ExpeditionStatus(2)
    EXPEDITION_FINISHED = ExpeditionStatus(3)

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
        self.schedule(self.alarm_time(time(hour=0)), self.farm_expeditions)
        self.schedule(self.alarm_time(time(hour=8)), self.farm_daily_bonus)
        self.schedule(self.alarm_time(time(hour=8)), self.buy_chest)
        self.schedule(self.alarm_time(time(hour=9)), self.farm_quests)
        self.schedule(self.alarm_time(time(hour=10)), self.farm_mail)
        self.schedule(self.alarm_time(time(hour=14)), self.farm_quests)
        self.schedule(self.alarm_time(time(hour=21)), self.farm_quests)

        logger.info('🤖 Running action queue.')
        while self.queue:
            when, _, action, args = heapq.heappop(self.queue)  # type: TQueueItem
            sleep_timedelta = when - self.now()
            sleep_duration = sleep_timedelta.total_seconds()
            if sleep_duration > 0.0:
                logger.info('💤 Next action %s%s in %s at %s', action.__name__, args, sleep_timedelta, when)
                sleep(sleep_duration)
            try:
                action(when, *args)
            except InvalidSessionError:
                logger.warning('😱 Invalid session.')
                self.api.authenticate()
                self.schedule(self.now(), action, *args)
            except AlreadyError:
                logger.info('🤔 Already done.')
            except InvalidResponseError as e:
                logger.error('😱 API returned something bad: %s', e)
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
            logger.info('📈 %s', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_daily_bonus)

    def farm_expeditions(self, when: datetime):
        logger.info('💰 Farming expeditions.')
        try:
            expeditions = self.api.list_expeditions()
            for expedition in expeditions:
                if expedition.status == self.EXPEDITION_COLLECT_REWARD:
                    reward = self.api.farm_expedition(expedition.id)
                    logger.info('📈 %s', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_expeditions)

    def farm_quests(self, when: datetime):
        logger.info('💰 Farming quests.')
        try:
            quests = self.api.get_all_quests()
            for quest in quests:
                if quest.state == self.QUEST_COLLECT_REWARD:
                    logger.info('📈 %s', self.api.farm_quest(quest.id))
        finally:
            self.schedule(when + self.ONE_DAY, self.farm_quests)

    def farm_mail(self, when: datetime):
        logger.info('💰 Farming mail')
        try:
            letters = self.api.get_all_mail()
            if not letters:
                return
            rewards = self.api.farm_mail(int(letter.id) for letter in letters)
            for reward in rewards.values():
                logger.info('📈 %s', reward)
        finally:
            self.schedule(when + timedelta(hours=6), self.farm_mail)

    def buy_chest(self, when: datetime):
        logger.info('📦 Buy chest.')
        try:
            for reward in self.api.buy_chest():
                logger.info('📈 %s', reward)
        finally:
            self.schedule(when + self.ONE_DAY, self.buy_chest)
