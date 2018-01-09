import contextlib
import json
from datetime import datetime, timedelta, timezone, tzinfo
from time import sleep
from typing import Any, Dict, Callable, Iterable, List, NamedTuple, Optional, Set, Tuple, Union

from bestmobabot import constants, responses
from bestmobabot.api import AlreadyError, API, InvalidResponseError, NotEnoughError
from bestmobabot.logger import logger
from bestmobabot.vk import VK

WhenCallable = Callable[[datetime], datetime]


class Task(NamedTuple):
    when: WhenCallable
    execute: Callable
    args: Tuple = ()

    def __str__(self):
        return f'{self.execute.__name__}{self.args}'

    @staticmethod
    def fixed_time(*, hour: int, minute: int, tz: Optional[tzinfo] = timezone.utc) -> WhenCallable:
        def should_execute(since: datetime) -> datetime:
            since = since.astimezone(tz)
            upcoming = since.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return upcoming if upcoming > since else upcoming + timedelta(days=1)
        return should_execute

    @staticmethod
    def every_n_seconds(seconds: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> WhenCallable:
        def should_execute(since: datetime) -> datetime:
            since = since.astimezone(tz)
            return since + timedelta(seconds=(seconds - (since.timestamp() - offset.total_seconds()) % seconds))
        return should_execute

    @staticmethod
    def every_n_minutes(minutes: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> WhenCallable:
        return Task.every_n_seconds(minutes * 60.0, tz=tz, offset=offset)

    @staticmethod
    def every_n_hours(hours: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> WhenCallable:
        return Task.every_n_minutes(hours * 60.0, tz=tz, offset=offset)


class Bot(contextlib.AbstractContextManager):
    MAX_OPEN_ARTIFACT_CHESTS = 5

    def __init__(self, api: API):
        self.api = api
        self.vk = VK()
        self.user: responses.User = None
        self.collected_gift_ids: Set[str] = set()
        self.tasks: List[Task] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.vk.__exit__(exc_type, exc_val, exc_tb)

    @property
    def state(self) -> Dict[str, Any]:
        return {
            'user': json.dumps(self.user.item),
            'collected_gift_ids': list(self.collected_gift_ids),
            'description': {
                'name': self.user.name,
            },
        }

    def start(self, state: Optional[Dict[str, Any]]):
        if state:
            self.user = responses.User.parse(json.loads(state['user']))
            self.collected_gift_ids = set(state['collected_gift_ids'])
        else:
            self.user = self.api.get_user_info()

        self.tasks = [
            # Stamina quests depend on player's time zone.
            Task(when=Task.fixed_time(hour=9, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(when=Task.fixed_time(hour=14, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(when=Task.fixed_time(hour=21, minute=30, tz=self.user.tz), execute=self.farm_quests),
            # Other quests are simultaneous for everyone. Day starts at 4:00 UTC.
            Task(when=Task.every_n_minutes(24 * 60 // 5, offset=timedelta(hours=-1)), execute=self.attack_arena),
            Task(when=Task.every_n_hours(6, offset=timedelta(minutes=15)), execute=self.farm_mail),
            Task(when=Task.every_n_hours(6, offset=timedelta(minutes=30)), execute=self.check_freebie),
            Task(when=Task.fixed_time(hour=3, minute=0), execute=self.farm_expeditions),
            Task(when=Task.fixed_time(hour=8, minute=0), execute=self.farm_daily_bonus),
            Task(when=Task.fixed_time(hour=8, minute=30), execute=self.buy_chest),
            Task(when=Task.fixed_time(hour=9, minute=0), execute=self.send_daily_gift),
            Task(when=Task.fixed_time(hour=10, minute=0), execute=self.farm_zeppelin_gift),

            # Debug tasks. Uncomment when needed.
            # Task(when=Task.every_n_minutes(1), execute=self.quack, args=('Quack 1!',)),
            # Task(when=Task.every_n_minutes(1), execute=self.quack, args=('Quack 2!',)),
            # Task(when=Task.fixed_time(hour=22, minute=14, tz=None), execute=self.quack, args=('Fixed time!',)),
        ]

    def run(self):
        # Initialise the execution time for each task.
        logger.info('🤖 Initialising task queue.')
        now = datetime.now().astimezone()
        next_execution = [task.when(now) for task in self.tasks]

        logger.info('🤖 Running task queue.')
        while True:
            # Find the earliest task.
            when, index = min((when, index) for index, when in enumerate(next_execution))
            task = self.tasks[index]
            logger.info('💤 Next is %s at %s local time.', task, when.astimezone().strftime('%H:%M:%S'))
            # Sleep until the execution time.
            sleep_time = (when - datetime.now().astimezone()).total_seconds()
            if sleep_time >= 0.0:
                sleep(sleep_time)
            # Execute the task.
            self.execute(task)
            # Update its execution time.
            next_execution[index] = task.when(max(datetime.now().astimezone(), when + timedelta(seconds=1)))

    def execute(self, task: Task):
        self.api.last_responses.clear()
        try:
            task.execute(*task.args)
        except AlreadyError as e:
            logger.info('🤔 Already done: %s.', e.description)
        except NotEnoughError as e:
            logger.info('🤔 Not enough: %s.', e.description)
        except InvalidResponseError as e:
            logger.error('😱 API returned something bad:')
            logger.error('😱 %s', e)
        except Exception as e:
            logger.critical('😱 Uncaught error.', exc_info=e)
            for result in self.api.last_responses:
                logger.critical('💬 API result: %s', result.strip())
        else:
            logger.info('✅ Well done.')

    @staticmethod
    def print_reward(reward: responses.Reward):
        logger.info('📈 %s', reward)

    @staticmethod
    def print_rewards(rewards: Iterable[responses.Reward]):
        for reward in rewards:
            Bot.print_reward(reward)

    @staticmethod
    def get_power(enemy: Union[responses.ArenaEnemy, responses.Hero]) -> int:
        return enemy.power

    # Actual tasks.
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def quack(text: str = 'Quack!'):
        """
        Отладочная задача.
        """
        logger.info('🦆 %s', text)
        sleep(1.0)

    def farm_daily_bonus(self):
        """
        Забирает ежедневный подарок.
        """
        logger.info('💰 Farming daily bonus…')
        self.print_reward(self.api.farm_daily_bonus())

    def farm_expeditions(self):
        """
        Собирает награду с экспедиций в дирижабле.
        """
        logger.info('💰 Farming expeditions…')
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.status == constants.EXPEDITION_COLLECT_REWARD:
                self.print_reward(self.api.farm_expedition(expedition.id))

    def farm_quests(self, quests: responses.Quests = None):
        """
        Собирает награды из заданий.
        """
        logger.info('💰 Farming quests…')
        quests = quests or self.api.get_all_quests()
        for quest in quests:
            if quest.state == constants.QUEST_COLLECT_REWARD:
                self.print_reward(self.api.farm_quest(quest.id))

    def farm_mail(self):
        """
        Собирает награды из почты.
        """
        logger.info('📩 Farming mail…')
        letters = self.api.get_all_mail()
        if not letters:
            return
        logger.info('📩 %s letters.', len(letters))
        self.print_rewards(self.api.farm_mail(int(letter.id) for letter in letters).values())

    def buy_chest(self):
        """
        Открывает ежедневный бесплатный сундук.
        """
        logger.info('📦 Buying chest…')
        self.print_rewards(self.api.buy_chest())

    def send_daily_gift(self):
        """
        Отправляет сердечки друзьям.
        """
        logger.info('🎁 Sending daily gift…')
        self.farm_quests(self.api.send_daily_gift(['15664420', '209336881', '386801200']))

    def attack_arena(self, when: datetime):
        """
        Совершает бой на арене.
        """
        logger.info('👊 Attacking arena…')

        # Find the best enemy.
        enemy = min([
            enemy
            for enemy in self.api.find_arena_enemies()
            if enemy.user is not None and not enemy.user.is_from_clan(self.user.clan_id)
        ], key=self.get_power)

        # Find the most powerful heroes.
        heroes = sorted(self.api.get_all_heroes(), key=self.get_power, reverse=True)[:5]

        # Attack and collect results.
        result, quests = self.api.attack_arena(enemy.user.id, [hero.id for hero in heroes])
        battle = result.battles[0]
        logger.info('👊 Win: %s %s %s ➡ %s', result.win, '⭐' * battle.stars, battle.old_place, battle.new_place)
        self.farm_quests(quests)

    def check_freebie(self):
        """
        Собирает подарки на странице игры ВКонтакте.
        """
        logger.info('🎁 Checking freebie…')
        gift_ids = set(self.vk.find_gifts()) - self.collected_gift_ids
        should_farm_mail = False

        for gift_id in gift_ids:
            logger.info('🎁 Checking %s…', gift_id)
            if self.api.check_freebie(gift_id) is not None:
                logger.info('🎉 Received %s!', gift_id)
                should_farm_mail = True
            self.collected_gift_ids.add(gift_id)

        if should_farm_mail:
            self.farm_mail()

    def farm_zeppelin_gift(self, when: datetime):
        """
        Собирает ключ у валькирии и открывает артефактные сундуки.
        """
        self.print_reward(self.api.farm_zeppelin_gift())
        for _ in range(self.MAX_OPEN_ARTIFACT_CHESTS):
            try:
                self.print_rewards(self.api.open_artifact_chest())
            except NotEnoughError:
                logger.info('💬 All keys are spent.')
                break
        else:
            logger.info('💬 All chests have been opened.')
