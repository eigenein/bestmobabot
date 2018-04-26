"""
The bot logic.
"""

import contextlib
import os
import pickle
from datetime import datetime, timedelta, tzinfo
from operator import attrgetter
from random import choice
from time import sleep
from typing import Callable, Iterable, List, NamedTuple, Optional, Set, Tuple

from bestmobabot import arena, constants
from bestmobabot.api import AlreadyError, API, InvalidResponseError, NotEnoughError, NotFoundError, OutOfRetargetDelta
from bestmobabot.database import Database
from bestmobabot.enums import *
from bestmobabot.logger import log_arena_result, log_heroes, log_reward, log_rewards, logger
from bestmobabot.model import Model
from bestmobabot.resources import mission_name, shop_name
from bestmobabot.responses import *
from bestmobabot.trainer import Trainer
from bestmobabot.vk import VK

NextRunAtCallable = Callable[[datetime], datetime]


class Task(NamedTuple):
    next_run_at: NextRunAtCallable
    execute: Callable[..., Optional[datetime]]
    args: Tuple = ()

    def __str__(self):
        return f'{self.execute.__name__}{self.args}'

    @staticmethod
    def at(*, hour: int, minute: int, tz: Optional[tzinfo] = None) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            since = since.astimezone(tz)
            upcoming = since.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return upcoming if upcoming > since else upcoming + timedelta(days=1)
        return next_run_at

    @staticmethod
    def every_n_seconds(seconds: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        def next_run_at(since: datetime) -> datetime:
            return since + timedelta(seconds=(seconds - (since.timestamp() - offset.total_seconds()) % seconds))
        return next_run_at

    @staticmethod
    def every_n_minutes(minutes: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_seconds(minutes * 60.0, offset)

    @staticmethod
    def every_n_hours(hours: float, offset: timedelta = timedelta()) -> NextRunAtCallable:
        return Task.every_n_minutes(hours * 60.0, offset)

    @staticmethod
    def asap() -> NextRunAtCallable:
        """
        Executes task as soon as possible. Only used for development.
        """
        def next_run_at(since: datetime) -> datetime:
            return since
        return next_run_at


class TaskNotAvailable(Exception):
    """
    Raised when task pre-conditions are not met.
    """


class BotHelper:
    """
    Helper methods.
    """
    db: Database
    api: API

    @staticmethod
    def get_hero_ids(heroes: Iterable[Hero]) -> List[str]:
        return [hero.id for hero in heroes]

    @staticmethod
    def naive_select_attackers(heroes: Iterable[Hero], count: int = constants.TEAM_SIZE) -> List[Hero]:
        """
        Selects the most powerful heroes.
        """
        return sorted(heroes, key=attrgetter('power'), reverse=True)[:count]

    def get_model(self) -> Optional[Model]:
        """
        Loads a predictive model from the database.
        """
        logger.info('🤖 Loading model…')
        return self.db.get_by_key('bot', 'model', loads=lambda value: pickle.loads(bytes.fromhex(value)))

    def check_arena(self, min_hero_count: int) -> Tuple[Model, List[Hero]]:
        """
        Checks pre-conditions for arena.
        """
        model = self.get_model()
        if not model:
            raise TaskNotAvailable('model is not ready yet')

        heroes = self.api.get_all_heroes()
        if len(heroes) < min_hero_count:
            raise TaskNotAvailable('not enough heroes')

        return model, heroes


class Bot(contextlib.AbstractContextManager, BotHelper):
    def __init__(
        self,
        db: Database,
        api: API,
        vk: VK,
        no_experience: bool,
        is_trainer: bool,
        raids: List[Tuple[str, int]],
        shops: List[Tuple[str, str]],
        arena_offset: timedelta,
    ):
        self.db = db
        self.api = api
        self.vk = vk
        self.no_experience = no_experience
        self.is_trainer = is_trainer
        self.raids = raids
        self.shops = shops
        self.arena_offset = arena_offset

        self.user: User = None
        self.tasks: List[Task] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.vk.__exit__(exc_type, exc_val, exc_tb)

    # Task engine.
    # ------------------------------------------------------------------------------------------------------------------

    def start(self):
        user_raw = self.db.get_by_key(f'bot:{self.api.user_id}', 'user.raw')
        if user_raw:
            self.user = User(user_raw)
        else:
            self.user = self.api.get_user_info()
            self.db.set(f'bot:{self.api.user_id}', 'user.raw', self.user.raw)

        self.tasks = [
            # These tasks depend on player's time zone.
            Task(next_run_at=Task.at(hour=8, minute=0, tz=self.user.tz), execute=self.register),
            Task(next_run_at=Task.at(hour=9, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=14, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=21, minute=30, tz=self.user.tz), execute=self.farm_quests),

            # Recurring tasks.
            Task(next_run_at=Task.every_n_minutes(24 * 60 // 5, self.arena_offset), execute=self.attack_arena),
            Task(next_run_at=Task.every_n_minutes(24 * 60 // 5, self.arena_offset), execute=self.attack_grand_arena),
            Task(next_run_at=Task.every_n_hours(6), execute=self.farm_mail),
            Task(next_run_at=Task.every_n_hours(6), execute=self.check_freebie),
            Task(next_run_at=Task.every_n_hours(6), execute=self.farm_expeditions),
            Task(next_run_at=Task.every_n_hours(8), execute=self.get_arena_replays),

            # One time a day.
            Task(next_run_at=Task.at(hour=6, minute=0), execute=self.skip_tower),
            Task(next_run_at=Task.at(hour=8, minute=0), execute=self.farm_daily_bonus),
            Task(next_run_at=Task.at(hour=8, minute=30), execute=self.buy_chest),
            Task(next_run_at=Task.at(hour=9, minute=0), execute=self.send_daily_gift),
            Task(next_run_at=Task.at(hour=10, minute=0), execute=self.farm_zeppelin_gift),

            # Debug tasks. Uncomment when needed.
            # Task(next_run_at=Task.every_n_minutes(1), execute=self.quack, args=('Quack 1!',)),
            # Task(next_run_at=Task.every_n_minutes(1), execute=self.quack, args=('Quack 2!',)),
            # Task(next_run_at=Task.at(hour=22, minute=14, tz=None), execute=self.quack, args=('Fixed time!',)),
            # Task(next_run_at=Task.at(hour=22, minute=40, tz=None), execute=self.shop, args=(['1'],)),
            # Task(next_run_at=Task.asap(), execute=self.check_freebie),
        ]
        for i, (mission_id, number) in enumerate(self.raids):
            self.tasks.append(Task(
                # FIXME: each mission is shifted by an hour to allow stamina to accumulate.
                next_run_at=Task.every_n_hours(24 / number, timedelta(hours=i)),
                execute=self.raid_mission,
                args=(mission_id,)),
            )
        if self.shops:
            self.tasks.extend([
                Task(next_run_at=Task.at(hour=11, minute=1), execute=self.shop, args=(['4', '5', '6', '9'],)),
                Task(next_run_at=Task.every_n_hours(8), execute=self.shop, args=(['1'],)),
            ])
        if self.is_trainer:
            self.tasks.append(Task(next_run_at=Task.at(hour=22, minute=0, tz=self.user.tz), execute=self.train_arena_model))

    def run(self):
        logger.info('🤖 Initialising task queue.')
        now = self.now()
        schedule = [task.next_run_at(now).astimezone() for task in self.tasks]

        logger.info('🤖 Running task queue.')
        while True:
            # Find the earliest task.
            run_at, index = min((run_at, index) for index, run_at in enumerate(schedule))
            task = self.tasks[index]
            logger.info(f'💤 Next is {task} at {run_at:%H:%M:%S}.')
            # Sleep until the execution time.
            sleep_time = (run_at - self.now()).total_seconds()
            if sleep_time >= 0.0:
                sleep(sleep_time)
            # Execute the task.
            next_run_at = self.execute(task) or task.next_run_at(max(self.now(), run_at + timedelta(seconds=1)))
            next_run_at = next_run_at.astimezone()  # keeping them in the local time zone
            # Update its execution time.
            logger.info(f'💤 Next run at {next_run_at:%H:%M:%S}.{os.linesep}')
            schedule[index] = next_run_at

    @staticmethod
    def now():
        return datetime.now().astimezone()

    def execute(self, task: Task) -> Optional[datetime]:
        self.api.last_responses.clear()
        try:
            next_run_at = task.execute(*task.args)
        except TaskNotAvailable as e:
            logger.warning(f'😐 Task unavailable: {e}.')
        except AlreadyError as e:
            logger.error(f'🤔 Already done: {e.description}.')
        except NotEnoughError as e:
            logger.error(f'🤔 Not enough: {e.description}.')
        except OutOfRetargetDelta:
            logger.error(f'🤔 Out of retarget delta.')
        except InvalidResponseError as e:
            logger.error('😱 API returned something bad:')
            logger.error(f'😱 {e}')
        except Exception as e:
            logger.critical('😱 Uncaught error.', exc_info=e)
            for result in self.api.last_responses:
                logger.critical(f'💬 API result: {result}')
        else:
            logger.info(f'✅ Well done.')
            return next_run_at

    # Tasks.
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def quack(text: str = 'Quack!'):
        """
        Отладочная задача.
        """
        logger.info(f'🦆 {text}')
        sleep(1.0)

    def register(self):
        """
        Заново заходит в игру, это нужно для появления ежедневных задач в событиях.
        """
        self.api.start(invalidate_session=True)
        self.api.register()

    def farm_daily_bonus(self):
        """
        Забирает ежедневный подарок.
        """
        logger.info('💰 Farming daily bonus…')
        log_reward(self.api.farm_daily_bonus())

    def farm_expeditions(self) -> Optional[datetime]:
        """
        Собирает награду с экспедиций в дирижабле.
        """
        now = self.now()

        logger.info('💰 Farming expeditions…')
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started and expedition.end_time < now:
                log_reward(self.api.farm_expedition(expedition.id))

        return self.send_expedition()  # farm expeditions once finished

    def send_expedition(self) -> Optional[datetime]:
        logger.info('👊 Sending an expedition…')

        # Check started expeditions.
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started:
                logger.info(f'✅ Started expedition ends at {expedition.end_time}.')
                return expedition.end_time

        # Get all busy heroes.
        busy_hero_ids = set.union(*(set(expedition.hero_ids) for expedition in expeditions))
        logger.info(f'👊 Busy heroes: {busy_hero_ids}.')

        # Choose the most powerful available heroes.
        heroes = self.naive_select_attackers(hero for hero in self.api.get_all_heroes() if hero.id not in busy_hero_ids)
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
        expedition = min(expeditions, key=attrgetter('duration'))  # choose the fastest expedition

        # Send the expedition.
        end_time, quests = self.api.send_expedition_heroes(expedition.id, self.get_hero_ids(heroes))
        logger.info(f'⏰ The expedition ends at {end_time}.')
        self.farm_quests(quests)
        return end_time

    def farm_quests(self, quests: Quests = None):
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
                logger.warning(f'🙈 Ignoring {quest.reward.experience} experience reward for quest #{quest.id}.')
                continue
            log_reward(self.api.farm_quest(quest.id))

    def farm_mail(self):
        """
        Собирает награды из почты.
        """
        logger.info('📩 Farming mail…')
        letters = self.api.get_all_mail()
        if not letters:
            return
        logger.info(f'📩 {len(letters)} letters.')
        log_rewards(self.api.farm_mail(letter.id for letter in letters).values())

    def buy_chest(self):
        """
        Открывает ежедневный бесплатный сундук.
        """
        logger.info('📦 Buying chest…')
        log_rewards(self.api.buy_chest())

    def send_daily_gift(self):
        """
        Отправляет сердечки друзьям.
        """
        logger.info('🎁 Sending daily gift…')
        self.farm_quests(self.api.send_daily_gift(['15664420', '209336881', '386801200', '386796029']))  # FIXME

    def train_arena_model(self):
        """
        Тренирует предсказательную модель для арены.
        """
        logger.info('🤖 Running trainer…')
        Trainer(self.db, n_splits=constants.MODEL_N_SPLITS, logger=logger).train()

    def attack_arena(self):
        """
        Совершает бой на арене.
        """
        logger.info('👊 Attacking arena…')
        model, heroes = self.check_arena(constants.TEAM_SIZE)

        # Pick an enemy and select attackers.
        enemy, attackers, probability = \
            arena.Arena(model, self.user.clan_id, heroes, self.api.find_arena_enemies).select_enemy()

        # Debugging.
        log_heroes('Attackers:', attackers)
        log_heroes('Defenders:', enemy.heroes)
        logger.info(f'👊 Enemy place: {enemy.place}.')
        logger.info(f'👊 Probability: {100.0 * probability:.1f}%.')

        # Attack!
        result, quests = self.api.attack_arena(enemy.user.id, self.get_hero_ids(attackers))

        # Collect results.
        log_arena_result(result)
        logger.info(f'👊 Current place: {result.arena_place}.')
        self.farm_quests(quests)

    def attack_grand_arena(self):
        """
        Совершает бой на гранд арене.
        """
        logger.info('👊 Attacking grand arena…')
        model, heroes = self.check_arena(constants.GRAND_SIZE)

        # Pick an enemy and select attackers.
        enemy, attacker_teams, probability = \
            arena.GrandArena(model, self.user.clan_id, heroes, self.api.find_grand_enemies).select_enemy()

        # Debugging.
        for i, (attackers, defenders) in enumerate(zip(attacker_teams, enemy.heroes), start=1):
            logger.info(f'👊 Battle #{i}.')
            log_heroes('Attackers:', attackers)
            log_heroes('Defenders:', defenders)
        logger.info(f'👊 Enemy place: {enemy.place}.')
        logger.info(f'👊 Probability: {100.0 * probability:.1f}%.')

        # Attack!
        result, quests = self.api.attack_grand(enemy.user.id, [
            [attacker.id for attacker in attackers]
            for attackers in attacker_teams
        ])

        # Collect results.
        log_arena_result(result)
        logger.info(f'👊 Current place: {result.grand_place}.')
        self.farm_quests(quests)
        log_reward(self.api.farm_grand_coins())

    def get_arena_replays(self):
        """
        Читает и сохраняет журналы арен.
        """
        logger.info('📒 Reading arena logs…')
        replays: List[Replay] = [
            *self.api.get_battle_by_type(BattleType.ARENA),
            *self.api.get_battle_by_type(BattleType.GRAND),
        ]
        for replay in replays:
            if self.db.exists('replays', replay.id):
                continue
            self.db.set('replays', replay.id, {
                'start_time': replay.start_time.timestamp(),
                'win': replay.win,
                'attackers': [hero.dump() for hero in replay.attackers],
                'defenders': [hero.dump() for defenders in replay.defenders for hero in defenders],
            })
            logger.info(f'📒 Saved #{replay.id}.')

    def check_freebie(self):
        """
        Собирает подарки на странице игры ВКонтакте.
        """
        logger.info('🎁 Checking freebie…')
        should_farm_mail = False

        for gift_id in self.vk.find_gifts():
            if self.db.exists(f'gifts:{self.api.user_id}', gift_id):
                continue
            logger.info(f'🎁 Checking {gift_id}…')
            reward = self.api.check_freebie(gift_id)
            if reward is not None:
                log_reward(reward)
                should_farm_mail = True
            self.db.set(f'gifts:{self.api.user_id}', gift_id, True)

        if should_farm_mail:
            self.farm_mail()

    def farm_zeppelin_gift(self):
        """
        Собирает ключ у валькирии и открывает артефактные сундуки.
        """
        logger.info('🎁 Farming zeppelin gift…')
        log_reward(self.api.farm_zeppelin_gift())
        for _ in range(constants.MAX_OPEN_ARTIFACT_CHESTS):
            try:
                log_rewards(self.api.open_artifact_chest())
            except NotEnoughError:
                logger.info('💬 All keys are spent.')
                break
        else:
            logger.info('💬 All chests have been opened.')

    def raid_mission(self, mission_id: str):
        """
        Ходит в рейд в миссию в кампании за предметами.
        """
        logger.info(f'👊 Raid mission «{mission_name(mission_id)}»…')
        log_rewards(self.api.raid_mission(mission_id))

    def shop(self, shop_ids: List[str]):
        """
        Покупает в магазине вещи.
        """
        logger.info(f'🛒 Refreshing shops {shop_ids}…')
        available_slots: Set[Tuple[str, str]] = {
            (shop_id, slot.id)
            for shop_id in shop_ids
            for slot in self.api.get_shop(shop_id)
            if not slot.is_bought
        }

        logger.info('🛒 Buying stuff…')
        for shop_id, slot_id in self.shops:
            if shop_id not in shop_ids:
                logger.debug(f'🛒 Ignoring shop «{shop_name(shop_id)}».')
                continue
            if (shop_id, slot_id) not in available_slots:
                logger.warning(f'🛒 Slot #{slot_id} is not available in shop «{shop_name(shop_id)}».')
                continue
            logger.info(f'🛒 Buying slot #{slot_id} in shop «{shop_name(shop_id)}»…')
            try:
                log_reward(self.api.shop(shop_id=shop_id, slot_id=slot_id))
            except NotEnoughError as e:
                logger.warning(f'🛒 Not enough: {e.description}')
            except AlreadyError as e:
                logger.warning(f'🛒 Already: {e.description}')

    def skip_tower(self):
        """
        Зачистка башни.
        """
        logger.info('🗼 Skipping the tower…')
        tower = self.api.get_tower_info()

        while tower.floor_number <= tower.may_skip_floor or not tower.is_battle:
            logger.info(f'🗼 Floor #{tower.floor_number}: {tower.floor_type}.')
            if tower.is_battle:
                tower, reward = self.api.skip_tower_floor()
                log_reward(reward)
            elif tower.is_chest:
                reward, _ = self.api.open_tower_chest(choice([0, 1, 2]))
                log_reward(reward)
                tower = self.api.next_tower_floor()
            elif tower.is_buff:
                # Buffs go from the cheapest to the most expensive.
                for buff_id in reversed(tower.buff_ids):
                    if buff_id not in constants.TOWER_IGNORED_BUFF_IDS:
                        try:
                            self.api.buy_tower_buff(buff_id)
                        except NotEnoughError:
                            logger.info(f'🗼 Not enough resources for buff #{buff_id}.')
                        except AlreadyError:
                            logger.info(f'🗼 Already bought buff #{buff_id}.')
                        except NotFoundError as e:
                            logger.warning(f'🗼 Not found for buff #{buff_id}: {e.description}.')
                    else:
                        logger.debug(f'🗼 Skip buff #{buff_id}.')
                tower = self.api.next_tower_floor()
            else:
                logger.error('🗼 Unknown floor type.')

    '''
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
    '''
