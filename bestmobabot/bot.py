import contextlib
import heapq
import json
from datetime import datetime, time, timedelta, timezone, tzinfo
from time import sleep
from typing import Any, Dict, Callable, Iterable, List, NamedTuple, Optional, Tuple

from bestmobabot import constants, responses
from bestmobabot.api import AlreadyError, API, InvalidResponseError, InvalidSessionError, InvalidSignatureError, NotEnoughError
from bestmobabot.utils import get_power, logger
from bestmobabot.vk import VK


class Task(NamedTuple):
    when: datetime
    index: int
    callable_: Callable
    args: Tuple


class Bot(contextlib.AbstractContextManager):
    DEFAULT_INTERVAL = timedelta(days=1)
    FARM_MAIL_INTERVAL = timedelta(hours=6)
    ARENA_INTERVAL = timedelta(minutes=(24 * 60 // 5))
    FREEBIE_INTERVAL = timedelta(hours=6)

    MAX_OPEN_ARTIFACT_CHESTS = 5

    def __init__(self, api: API):
        self.api = api
        self.user: responses.User = None
        self.queue: List[Task] = []
        self.task_counter = 0
        self.vk = VK()
        self.collected_gift_ids = set()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.vk.__exit__(exc_type, exc_val, exc_tb)

    @property
    def state(self) -> Dict[str, Any]:
        return {
            'user': json.dumps(self.user.item),
            'collected_gift_ids': list(self.collected_gift_ids),
            'task_counter': self.task_counter,
            'queue': [{
                'when': task.when.timestamp(),
                'index': task.index,
                'name': task.callable_.__name__,
                'args': task.args,
            } for task in self.queue],
        }

    def start(self, state: Optional[Dict[str, Any]]):
        if state:
            self.user = responses.User.parse(json.loads(state['user']))
            self.collected_gift_ids = set(state['collected_gift_ids'])
            self.task_counter = state['task_counter']
            for item in state['queue']:
                task = Task(
                    when=datetime.fromtimestamp(item['when']).astimezone(),
                    index=item['index'],
                    callable_=getattr(self, item['name']),
                    args=tuple(item['args']),
                )
                logger.info('⏰ Adding scheduled task %s%s at %s', task.callable_.__name__, task.args, task.when)
                self.queue.append(task)
            heapq.heapify(self.queue)
            return

        self.user = self.api.get_user_info()

        logger.info('🤖 Scheduling initial tasks.')

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

    def run(self):
        logger.info('🤖 Running task queue.')
        while self.queue:
            self.sleep_until(self.queue[0])
            self.api.last_responses.clear()
            self.execute(heapq.heappop(self.queue))

        logger.fatal('🏳 Task queue is empty.')

    @staticmethod
    def alarm_time(time_: time, *, tz: tzinfo = timezone.utc, interval=DEFAULT_INTERVAL) -> datetime:
        now = datetime.now(tz).replace(microsecond=0)
        dt = now.replace(hour=time_.hour, minute=time_.minute, second=time_.second)
        while dt < now:
            dt += interval
        return dt

    def schedule(self, when: datetime, callable_: Callable, *args: Any):
        self.task_counter += 1
        when = when.astimezone()
        logger.info('⏰ Schedule %s%s at %s', callable_.__name__, args, when)
        heapq.heappush(self.queue, Task(when=when, index=self.task_counter, callable_=callable_, args=args))

    @staticmethod
    def sleep_until(task: Task):
        sleep_timedelta = task.when - datetime.now(timezone.utc)
        sleep_duration = sleep_timedelta.total_seconds()
        if sleep_duration > 0.0:
            logger.info('💤 Next task is %s%s in %s at %s', task.callable_.__name__, task.args, sleep_timedelta, task.when)
            sleep(sleep_duration)

    def execute(self, task: Task):
        try:
            task.callable_(task.when, *task.args)
        except (InvalidSessionError, InvalidSignatureError) as e:
            logger.warning('😱 Invalid session: %s.', e)
            self.api.start(state=None)
            self.schedule(task.when, task.callable_, *task.args)
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

    @staticmethod
    def print_reward(reward: responses.Reward):
        logger.info('📈 %s', reward)

    @staticmethod
    def print_rewards(rewards: Iterable[responses.Reward]):
        for reward in rewards:
            Bot.print_reward(reward)

    # Actual tasks.
    # ------------------------------------------------------------------------------------------------------------------

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
