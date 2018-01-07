import contextlib
import heapq
from datetime import datetime, time, timedelta, timezone, tzinfo
from time import sleep
from typing import Any, Callable, Iterable, List, Tuple

from bestmobabot import constants, responses
from bestmobabot.api import AlreadyError, Api, InvalidResponseError, InvalidSessionError, NotEnoughError
from bestmobabot.utils import get_power, logger
from bestmobabot.vk import VK

TAction = Callable[..., Any]
TQueueItem = Tuple[datetime, int, TAction, Tuple]


class Bot(contextlib.AbstractContextManager):
    DEFAULT_INTERVAL = timedelta(days=1)
    FARM_MAIL_INTERVAL = timedelta(hours=6)
    ARENA_INTERVAL = timedelta(minutes=(24 * 60 // 5))
    FREEBIE_INTERVAL = timedelta(hours=6)

    MAX_OPEN_ARTIFACT_CHESTS = 5

    @staticmethod
    def start(api: Api) -> 'Bot':
        return Bot(api, api.get_user_info())

    def __init__(self, api: Api, user: responses.User):
        self.api = api
        self.user = user
        self.queue: List[TQueueItem] = []
        self.action_counter = 0
        self.vk = VK()
        self.collected_gift_ids = set()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.vk.__exit__(exc_type, exc_val, exc_tb)

    def run(self):
        logger.info('🤖 Scheduling initial actions.')

        # Stamina quests depend on player's time zone.
        self.schedule(self.alarm_time(time(hour=9, minute=30), tz=self.user.tz), self.farm_quests)
        self.schedule(self.alarm_time(time(hour=14, minute=30), tz=self.user.tz), self.farm_quests)
        self.schedule(self.alarm_time(time(hour=21, minute=30), tz=self.user.tz), self.farm_quests)

        # Other quests are simultaneous for everyone. Day starts at 4:00 UTC.
        self.schedule(self.alarm_time(time(hour=0, minute=0), interval=self.ARENA_INTERVAL), self.attack_arena)
        self.schedule(self.alarm_time(time(hour=1, minute=0), interval=self.FARM_MAIL_INTERVAL), self.farm_mail)
        self.schedule(self.alarm_time(time(hour=3, minute=0)), self.farm_expeditions)
        self.schedule(self.alarm_time(time(hour=8, minute=0)), self.farm_daily_bonus)
        self.schedule(self.alarm_time(time(hour=8, minute=30)), self.buy_chest)
        self.schedule(self.alarm_time(time(hour=9, minute=0)), self.send_daily_gift)
        self.schedule(self.alarm_time(time(hour=9, minute=30), interval=self.FREEBIE_INTERVAL), self.check_freebie)
        self.schedule(self.alarm_time(time(hour=10, minute=0)), self.farm_zeppelin_gift)

        logger.info('🤖 Running action queue.')
        while self.queue:
            when, _, action, args = heapq.heappop(self.queue)  # type: TQueueItem
            sleep_timedelta = when - datetime.now(timezone.utc)
            sleep_duration = sleep_timedelta.total_seconds()
            if sleep_duration > 0.0:
                logger.info('💤 Next action %s%s in %s at %s', action.__name__, args, sleep_timedelta, when)
                sleep(sleep_duration)
            self.api.last_responses.clear()
            try:
                action(when, *args)
            except InvalidSessionError:
                logger.warning('😱 Invalid session.')
                self.api.authenticate()
                self.schedule(when, action, *args)
            except AlreadyError:
                logger.info('🤔 Already done.')
            except InvalidResponseError as e:
                logger.error('😱 API returned something bad: %s', e)
            except Exception as e:
                logger.error('😱 Uncaught error.', exc_info=e)
                for result in self.api.last_responses:
                    logger.error('💬 API result: %s', result.strip())
            else:
                logger.info('✅ Well done.')

        logger.fatal('🏳 Action queue is empty.')

    @staticmethod
    def alarm_time(time_: time, *, tz: tzinfo = timezone.utc, interval=DEFAULT_INTERVAL) -> datetime:
        now = datetime.now(tz).replace(microsecond=0)
        dt = now.replace(hour=time_.hour, minute=time_.minute, second=time_.second)
        while dt < now:
            dt += interval
        return dt

    def schedule(self, when: datetime, action: TAction, *args: Any):
        self.action_counter += 1
        when = when.astimezone()
        logger.debug('⏰ Schedule %s%s at %s', action.__name__, args, when)
        heapq.heappush(self.queue, (when, self.action_counter, action, args))

    @staticmethod
    def print_reward(reward: responses.Reward):
        logger.info('📈 %s', reward)

    @staticmethod
    def print_rewards(rewards: Iterable[responses.Reward]):
        for reward in rewards:
            Bot.print_reward(reward)

    def farm_daily_bonus(self, when: datetime):
        """
        Забирает ежедневный подарок.
        """
        logger.info('💰 Farming daily bonus…')
        try:
            self.print_reward(self.api.farm_daily_bonus())
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.farm_daily_bonus)

    def farm_expeditions(self, when: datetime):
        """
        Собирает награду с экспедиций в дирижабле.
        """
        logger.info('💰 Farming expeditions…')
        try:
            expeditions = self.api.list_expeditions()
            for expedition in expeditions:
                if expedition.status == constants.EXPEDITION_COLLECT_REWARD:
                    self.print_reward(self.api.farm_expedition(expedition.id))
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.farm_expeditions)

    def farm_quests(self, when: datetime):
        """
        Собирает награды из заданий.
        """
        try:
            self._farm_quests(self.api.get_all_quests())
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.farm_quests)

    def _farm_quests(self, quests: responses.Quests):
        logger.info('💰 Farming quests…')
        for quest in quests:
            if quest.state == constants.QUEST_COLLECT_REWARD:
                self.print_reward(self.api.farm_quest(quest.id))

    def farm_mail(self, when: datetime):
        """
        Собирает награды из почты.
        """
        try:
            self._farm_mail()
        finally:
            self.schedule(when + self.FARM_MAIL_INTERVAL, self.farm_mail)

    def _farm_mail(self):
        logger.info('📩 Farming mail…')
        letters = self.api.get_all_mail()
        if not letters:
            return
        logger.info('📩 %s letters.', len(letters))
        self.print_rewards(self.api.farm_mail(int(letter.id) for letter in letters).values())

    def buy_chest(self, when: datetime):
        """
        Открывает ежедневный бесплатный сундук.
        """
        logger.info('📦 Buying chest…')
        try:
            self.print_rewards(self.api.buy_chest())
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.buy_chest)

    def send_daily_gift(self, when: datetime):
        """
        Отправляет сердечки друзьям.
        """
        logger.info('🎁 Sending daily gift…')
        try:
            self._farm_quests(self.api.send_daily_gift(['15664420', '209336881', '386801200']))
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.send_daily_gift)

    def attack_arena(self, when: datetime):
        """
        Совершает бой на арене.
        """
        logger.info('👊 Attacking arena…')
        try:
            enemy = min([
                enemy
                for enemy in self.api.find_arena_enemies()
                if not enemy.user.is_from_clan(self.user.clan_id)
            ], key=get_power)
            heroes = sorted(self.api.get_all_heroes(), key=get_power, reverse=True)[:5]
            result, quests = self.api.attack_arena(enemy.user.id, [hero.id for hero in heroes])
            battle = result.battles[0]
            logger.info('👊 Win: %s %s %s ➡ %s', result.win, '⭐' * battle.stars, battle.old_place, battle.new_place)
            self._farm_quests(quests)
        except NotEnoughError:
            logger.info('💬 Not enough.')
        finally:
            self.schedule(when + self.ARENA_INTERVAL, self.attack_arena)

    def check_freebie(self, when: datetime):
        """
        Собирает подарки на странице игры ВКонтакте.
        """
        logger.info('🎁 Checking freebie…')
        try:
            gift_ids = set(self.vk.find_gifts()) - self.collected_gift_ids
            should_farm_mail = False
            for gift_id in gift_ids:
                logger.info('🎁 Checking %s…', gift_id)
                if self.api.check_freebie(gift_id) is not None:
                    logger.info('🎉 Received %s!', gift_id)
                    should_farm_mail = True
            if should_farm_mail:
                self._farm_mail()
        finally:
            self.schedule(when + self.FREEBIE_INTERVAL, self.check_freebie)

    def farm_zeppelin_gift(self, when: datetime):
        """
        Собирает ключ у валькирии и открывает артефактные сундуки.
        """
        try:
            self.print_reward(self.api.farm_zeppelin_gift())
            for _ in range(self.MAX_OPEN_ARTIFACT_CHESTS):
                try:
                    self.print_rewards(self.api.open_artifact_chest())
                except NotEnoughError:
                    logger.info('💬 Not enough.')
                    break
            else:
                logger.info('💬 All chests have been opened.')
        finally:
            self.schedule(when + self.DEFAULT_INTERVAL, self.farm_zeppelin_gift)
