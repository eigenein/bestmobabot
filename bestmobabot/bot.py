import contextlib
import json
from datetime import datetime, timedelta, timezone, tzinfo
from time import sleep
from typing import Any, Dict, Callable, Iterable, List, NamedTuple, Optional, Set, TextIO, Tuple, Union

from bestmobabot import responses, types
from bestmobabot.api import AlreadyError, API, InvalidResponseError, NotEnoughError
from bestmobabot.logger import logger
from bestmobabot.vk import VK

NextRunAtCallable = Callable[[datetime], datetime]


class Task(NamedTuple):
    next_run_at: NextRunAtCallable
    execute: Callable[..., Optional[datetime]]
    args: Tuple = ()

    def __str__(self):
        return f'{self.execute.__name__}{self.args}'

    @staticmethod
    def at(*, hour: int, minute: int, tz: Optional[tzinfo] = timezone.utc) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            since = since.astimezone(tz)
            upcoming = since.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return upcoming if upcoming > since else upcoming + timedelta(days=1)
        return next_run_at

    @staticmethod
    def every_n_seconds(seconds: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            since = since.astimezone(tz)
            return since + timedelta(seconds=(seconds - (since.timestamp() - offset.total_seconds()) % seconds))
        return next_run_at

    @staticmethod
    def every_n_minutes(minutes: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_seconds(minutes * 60.0, tz=tz, offset=offset)

    @staticmethod
    def every_n_hours(hours: float, *, tz: Optional[tzinfo] = timezone.utc, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_minutes(hours * 60.0, tz=tz, offset=offset)


class Bot(contextlib.AbstractContextManager):
    MAX_OPEN_ARTIFACT_CHESTS = 5

    def __init__(self, api: API, no_experience: bool, battle_log: Optional[TextIO]):
        self.api = api
        self.no_experience = no_experience
        self.battle_log = battle_log
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
            # Re-registration task.
            Task(next_run_at=Task.at(hour=8, minute=0, tz=self.user.tz), execute=self.register),

            # Stamina quests depend on player's time zone.
            Task(next_run_at=Task.at(hour=9, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=14, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=21, minute=30, tz=self.user.tz), execute=self.farm_quests),

            # Other quests are simultaneous for everyone. Day starts at 3:00 UTC.
            Task(next_run_at=Task.every_n_minutes(24 * 60 // 5, offset=timedelta(hours=-1)), execute=self.attack_arena),
            Task(next_run_at=Task.every_n_hours(6, offset=timedelta(minutes=15)), execute=self.farm_mail),
            Task(next_run_at=Task.every_n_hours(6, offset=timedelta(minutes=30)), execute=self.check_freebie),
            Task(next_run_at=Task.at(hour=3, minute=0), execute=self.farm_expeditions),
            Task(next_run_at=Task.at(hour=8, minute=0), execute=self.farm_daily_bonus),
            Task(next_run_at=Task.at(hour=8, minute=30), execute=self.buy_chest),
            Task(next_run_at=Task.at(hour=9, minute=0), execute=self.send_daily_gift),
            Task(next_run_at=Task.at(hour=10, minute=0), execute=self.farm_zeppelin_gift),

            # Debug tasks. Uncomment when needed.
            # Task(next_run_at=Task.every_n_minutes(1), execute=self.quack, args=('Quack 1!',)),
            # Task(next_run_at=Task.every_n_minutes(1), execute=self.quack, args=('Quack 2!',)),
            # Task(next_run_at=Task.fixed_time(hour=22, minute=14, tz=None), execute=self.quack, args=('Fixed time!',)),
            # Task(next_run_at=Task.at(hour=14, minute=25), execute=self.farm_expeditions),
        ]

    def run(self):
        # Initialise the execution time for each task.
        logger.info('🤖 Initialising task queue.')
        now = datetime.now().astimezone()
        schedule = [task.next_run_at(now) for task in self.tasks]

        logger.info('🤖 Running task queue.')
        while True:
            # Find the earliest task.
            run_at, index = min((run_at, index) for index, run_at in enumerate(schedule))
            task = self.tasks[index]
            logger.info('💤 Next is %s at %s local time.', task, run_at.astimezone().strftime('%H:%M:%S'))
            # Sleep until the execution time.
            sleep_time = (run_at - datetime.now().astimezone()).total_seconds()
            if sleep_time >= 0.0:
                sleep(sleep_time)
            # Execute the task.
            next_run_at = self.execute(task)
            # Update its execution time.
            schedule[index] = next_run_at or task.next_run_at(max(datetime.now().astimezone(), run_at + timedelta(seconds=1)))

    def execute(self, task: Task) -> Optional[datetime]:
        self.api.last_responses.clear()
        try:
            next_run_at = task.execute(*task.args)
        except AlreadyError as e:
            logger.error('🤔 Already done: %s.', e.description)
        except NotEnoughError as e:
            logger.error('🤔 Not enough: %s.', e.description)
        except InvalidResponseError as e:
            logger.error('😱 API returned something bad:')
            logger.error('😱 %s', e)
        except Exception as e:
            logger.critical('😱 Uncaught error.', exc_info=e)
            for result in self.api.last_responses:
                logger.critical('💬 API result: %s', result)
        else:
            logger.info('✅ Well done.')
            return next_run_at

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

    @staticmethod
    def get_item(response: Union[responses.User, responses.Hero]) -> Dict:
        return response.item

    @staticmethod
    def get_duration(expedition: responses.Expedition) -> timedelta:
        return expedition.duration

    def get_most_powerful_team(self, heroes: Iterable[responses.Hero]) -> List[responses.Hero]:
        return sorted(heroes, key=self.get_power, reverse=True)[:5]

    @staticmethod
    def get_hero_ids(heroes: Iterable[responses.Hero]) -> types.HeroIDs:
        return [hero.id for hero in heroes]

    # Actual tasks.
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def quack(text: str = 'Quack!'):
        """
        Отладочная задача.
        """
        logger.info('🦆 %s', text)
        sleep(1.0)

    def register(self):
        """
        Заново заходит в игру, это нужно для появления ежедневных задач в событиях.
        """
        self.api.start(state=None)
        self.api.register()

    def farm_daily_bonus(self):
        """
        Забирает ежедневный подарок.
        """
        logger.info('💰 Farming daily bonus…')
        self.print_reward(self.api.farm_daily_bonus())

    def farm_expeditions(self) -> Optional[datetime]:
        """
        Собирает награду с экспедиций в дирижабле.
        """
        now = datetime.now().astimezone()

        logger.info('💰 Farming expeditions…')
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started and expedition.end_time < now:
                self.print_reward(self.api.farm_expedition(expedition.id))

        return self.send_expedition()  # farm expeditions once finished

    def send_expedition(self) -> Optional[datetime]:
        logger.info('👊 Sending an expedition…')

        # Check started expeditions.
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started:
                logger.info('✅ Started expedition ends at %s.', expedition.end_time)
                return expedition.end_time

        # Get all busy heroes.
        busy_hero_ids = set.union(*(set(expedition.hero_ids) for expedition in expeditions))
        logger.info('👊 Busy heroes: %s.', busy_hero_ids)

        # Choose the most powerful available heroes.
        heroes = self.get_most_powerful_team(hero for hero in self.api.get_all_heroes() if hero.id not in busy_hero_ids)
        if not heroes:
            logger.info('✅ No heroes available.')
            return None
        team_power = sum(hero.power for hero in heroes)

        # Find available expeditions.
        expeditions = [
            expedition
            for expedition in self.api.list_expeditions()
            if expedition.is_available and expedition.power <= team_power
        ]
        if not expeditions:
            logger.info('✅ No expeditions available.')
            return None
        expedition = min(expeditions, key=self.get_duration)  # choose the fastest expedition

        # Send the expedition.
        end_time, quests = self.api.send_expedition_heroes(expedition.id, self.get_hero_ids(heroes))
        logger.info('⏰ The expedition ends at %s.', end_time)
        self.farm_quests(quests)
        return end_time

    def farm_quests(self, quests: responses.Quests = None):
        """
        Собирает награды из заданий.
        """
        logger.info('💰 Farming quests…')
        if quests is None:
            quests = self.api.get_all_quests()
        for quest in quests:
            if not quest.is_reward_available:
                continue
            if self.no_experience and quest.reward.experience:
                logger.warning('🙈 Ignoring %s experience reward for quest %s.', quest.reward.experience, quest.id)
                continue
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
        self.farm_quests(self.api.send_daily_gift(['15664420', '209336881', '386801200', '386796029']))

    def attack_arena(self):
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

        # Attack and collect results.
        heroes = self.get_most_powerful_team(self.api.get_all_heroes())
        result, quests = self.api.attack_arena(enemy.user.id, self.get_hero_ids(heroes))
        battle = result.battles[0]
        if result.win:
            logger.info('🎉 %s %s ➡ %s', '⭐' * battle.stars, battle.old_place, battle.new_place)
        else:
            logger.info('😞 You lose!')
        self.print_reward(result.reward)
        self.farm_quests(quests)

        # Save battle result.
        if self.battle_log:
            print(json.dumps({
                'win': result.win,
                'stars': battle.stars,
                'player': [self.get_item(hero) for hero in heroes],
                'enemies': [self.get_item(hero) for hero in enemy.heroes],
            }), file=self.battle_log)
            self.battle_log.flush()

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

    def farm_zeppelin_gift(self):
        """
        Собирает ключ у валькирии и открывает артефактные сундуки.
        """
        logger.info('🎁 Farming zeppelin gift…')
        self.print_reward(self.api.farm_zeppelin_gift())
        for _ in range(self.MAX_OPEN_ARTIFACT_CHESTS):
            try:
                self.print_rewards(self.api.open_artifact_chest())
            except NotEnoughError:
                logger.info('💬 All keys are spent.')
                break
        else:
            logger.info('💬 All chests have been opened.')

    def attack_boss(self):
        """
        Выполняет бой в Запределье.
        """
        logger.info('👊 Attacking a boss…')

        # Get current boss.
        boss, *_ = self.api.get_current_boss()
        logger.info('👊 Boss %s.', boss.id)

        # Find appropriate heroes.
        heroes = sorted([
            hero
            for hero in self.api.get_all_heroes()
            if hero.id in API.RECOMMENDED_HEROES[boss.id]
        ], key=self.get_power, reverse=True)[:5]
        if not heroes:
            logger.warning('😞 No appropriate heroes.')
            return

        # Attack boss.
        hero_ids = self.get_hero_ids(heroes)
        battle = self.api.attack_boss(boss.id, hero_ids)
        logger.warning('👊 Seed %s.', battle.seed)
        self.api.sleep(20.0)
        quests = self.api.end_boss_battle(battle.seed, hero_ids)

        # Farm rewards.
        self.farm_quests(quests)
        reward, quests = self.api.open_boss_chest(boss.id)
        self.print_reward(reward)
        self.farm_quests(quests)
