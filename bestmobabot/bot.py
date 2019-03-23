import pickle
from base64 import b85decode
from calendar import SATURDAY
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from operator import attrgetter
from random import choice, shuffle
from time import sleep
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from bestmobabot import constants
from bestmobabot.api import API, AlreadyError, NotEnoughError, NotFoundError
from bestmobabot.arena import ArenaSolution, ArenaSolver, reduce_grand_arena, reduce_normal_arena
from bestmobabot.database import Database
from bestmobabot.dataclasses_ import (
    ArenaResult,
    Dungeon,
    EndDungeonBattleResponse,
    Hero,
    Mission,
    Quest,
    Quests,
    Replay,
    Reward,
    User,
)
from bestmobabot.enums import BattleType, DungeonUnitType, HeroesJSMode, LibraryTitanElement, TowerFloorType
from bestmobabot.helpers import find_expedition_team, get_teams_unit_ids, get_unit_ids, naive_select_attackers
from bestmobabot.jsapi import NotEnoughStars, execute_battle_with_retry
from bestmobabot.logging_ import log_rewards, logger
from bestmobabot.model import Model
from bestmobabot.resources import get_heroic_mission_ids, mission_name, shop_name
from bestmobabot.scheduler import Scheduler, Task, now
from bestmobabot.settings import Settings
from bestmobabot.telegram import Telegram, TelegramLogger
from bestmobabot.tracking import send_event
from bestmobabot.trainer import Trainer
from bestmobabot.vk import VK


class Bot:
    def __init__(self, db: Database, api: API, vk: VK, telegram: Optional[Telegram], settings: Settings):
        self.db = db
        self.api = api
        self.vk = vk
        self.logger = TelegramLogger(telegram)
        self.settings = settings

        self.user: User = None
        self.scheduler = Scheduler(self)

    # Task engine.
    # ------------------------------------------------------------------------------------------------------------------

    def prepare(self):
        self.user = self.api.get_user_info()

        self.scheduler.add_tasks([
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=4, minute=48, tzinfo=self.user.tz),
                time(hour=9, minute=36, tzinfo=self.user.tz),
                time(hour=14, minute=24, tzinfo=self.user.tz),
                time(hour=19, minute=12, tzinfo=self.user.tz),
            ], execute=self.attack_normal_arena, offset=self.settings.bot.arena.schedule_offset),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=4, minute=48, tzinfo=self.user.tz),
                time(hour=9, minute=36, tzinfo=self.user.tz),
                time(hour=14, minute=24, tzinfo=self.user.tz),
                time(hour=19, minute=12, tzinfo=self.user.tz),
            ], execute=self.attack_grand_arena, offset=self.settings.bot.arena.schedule_offset),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=6, minute=0, tzinfo=self.user.tz),
                time(hour=12, minute=0, tzinfo=self.user.tz),
                time(hour=18, minute=0, tzinfo=self.user.tz),
            ], execute=self.farm_mail),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=6, minute=0, tzinfo=self.user.tz),
                time(hour=12, minute=0, tzinfo=self.user.tz),
                time(hour=18, minute=0, tzinfo=self.user.tz),
            ], execute=self.check_freebie),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=8, minute=0, tzinfo=self.user.tz),
                time(hour=16, minute=0, tzinfo=self.user.tz),
            ], execute=self.farm_expeditions),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=12, minute=0, tzinfo=self.user.tz),
            ], execute=self.get_arena_replays),
            Task(at=[
                time(hour=0, minute=0, tzinfo=self.user.tz),
                time(hour=3, minute=0, tzinfo=self.user.tz),
                time(hour=6, minute=0, tzinfo=self.user.tz),
                time(hour=9, minute=0, tzinfo=self.user.tz),
                time(hour=12, minute=0, tzinfo=self.user.tz),
                time(hour=15, minute=0, tzinfo=self.user.tz),
                time(hour=18, minute=0, tzinfo=self.user.tz),
                time(hour=21, minute=0, tzinfo=self.user.tz),
            ], execute=self.raid_missions),
            Task(at=[
                time(hour=9, minute=30, tzinfo=self.user.tz),
                time(hour=14, minute=30, tzinfo=self.user.tz),
                time(hour=21, minute=30, tzinfo=self.user.tz),
            ], execute=self.farm_quests),

            Task(at=[time(hour=6, minute=0, tzinfo=self.user.tz)], execute=self.skip_tower),
            Task(at=[time(hour=8, minute=0, tzinfo=self.user.tz)], execute=self.register),
            Task(at=[time(hour=8, minute=15, tzinfo=self.user.tz)], execute=self.farm_daily_bonus),
            Task(at=[time(hour=8, minute=20, tzinfo=timezone.utc)], execute=self.raid_bosses),
            Task(at=[time(hour=8, minute=30, tzinfo=self.user.tz)], execute=self.buy_chest),
            Task(at=[time(hour=8, minute=40, tzinfo=timezone.utc)], execute=self.hall_of_fame),
            Task(at=[time(hour=8, minute=45, tzinfo=self.user.tz)], execute=self.level_up_titan_hero_gift),
            Task(at=[time(hour=9, minute=0, tzinfo=self.user.tz)], execute=self.send_daily_gift),
            Task(at=[time(hour=9, minute=15, tzinfo=self.user.tz)], execute=self.open_titan_artifact_chest),
            Task(at=[time(hour=9, minute=30, tzinfo=self.user.tz)], execute=self.farm_offers),
            Task(at=[time(hour=10, minute=0, tzinfo=self.user.tz)], execute=self.farm_zeppelin_gift),
            Task(at=[time(hour=10, minute=15, tzinfo=self.user.tz)], execute=self.clear_dungeon),
        ])
        if self.settings.bot.shops:
            self.scheduler.add_task(Task(at=[
                # First shopping time should be later than usual event start time (2:00 UTC).
                # Every 8 hours afterwards.
                time(hour=2, minute=15, tzinfo=timezone.utc),
                time(hour=10, minute=15, tzinfo=timezone.utc),
                time(hour=18, minute=15, tzinfo=timezone.utc),
            ], execute=self.shop))
        if self.settings.bot.is_trainer:
            self.scheduler.add_task(Task(at=[time(hour=22, minute=0)], execute=self.train_arena_model))
        if self.settings.bot.arena.randomize_grand_defenders:
            self.scheduler.add_task(Task(at=[time(hour=10, minute=30)], execute=self.randomize_grand_defenders))
        if self.settings.bot.enchant_rune:
            self.scheduler.add_task(Task(at=[time(hour=9, minute=0)], execute=self.enchant_rune))
        if self.settings.bot.debug:
            logger.warning('Running in debug mode.')
            self.scheduler.add_task(Task(at=[(datetime.now() + timedelta(seconds=15)).time()], execute=self.quack))

        send_event(category='bot', action='start', user_id=self.api.user_id)

    def run(self):
        self.scheduler.run()

    # Helpers.
    # ------------------------------------------------------------------------------------------------------------------

    def log(self, text: str, pin=False):
        self.logger.append(text)
        self.logger.flush(pin)

    def get_raid_mission_ids(self) -> Iterable[str]:
        missions: Dict[str, Mission] = {
            mission.id: mission
            for mission in self.api.get_all_missions()
            if mission.is_raid_available and mission_name(mission.id).lower() in self.settings.bot.raid_missions
        }

        # Get heroic mission IDs.
        heroic_mission_ids = get_heroic_mission_ids()

        # First, yield heroic missions.
        raided_heroic_mission_ids = list(missions.keys() & heroic_mission_ids)
        shuffle(raided_heroic_mission_ids)  # shuffle in order to distribute stamina evenly
        logger.info(f'Raided heroic missions: {raided_heroic_mission_ids}.')
        for mission_id in raided_heroic_mission_ids:
            tries_left = constants.RAID_N_HEROIC_TRIES - missions[mission_id].tries_spent
            logger.info(f'Mission #{mission_id}: {tries_left} tries left.')
            for _ in range(tries_left):
                yield mission_id

        # Then, randomly choose non-heroic missions infinitely.
        non_heroic_mission_ids = list(missions.keys() - heroic_mission_ids)
        logger.info(f'Raided non-heroic missions: {non_heroic_mission_ids}.')
        if not non_heroic_mission_ids:
            logger.info('No raided non-heroic missions.')
            return
        while True:
            yield choice(non_heroic_mission_ids)

    def run_manual_mission(self, mission_id: str, hero_ids: List[str], n_retries=3, n_stars=1):
        """
        Attacks the specified mission with the specified heroes.
        Supposed to be used in the shell.
        """
        try:
            reward = execute_battle_with_retry(
                mode=HeroesJSMode.TOWER,
                start_battle=lambda: self.api.start_mission(mission_id, hero_ids),
                end_battle=lambda response: self.api.end_mission(mission_id, response),
                n_retries=n_retries,
                n_stars=n_stars,
            )
        except NotEnoughStars:
            logger.error('Not enough stars.')
        else:
            reward.log()

    # Tasks.
    # ------------------------------------------------------------------------------------------------------------------

    def quack(self):
        """
        Отладочная задача.
        """
        logger.info('About to quack…')
        self.log(f'🐤 *{self.user.name}* собирается крякать…')
        sleep(5)
        logger.info('Quack!')
        self.log(f'🐤 Бот *{self.user.name}* сказал: «Кря!»')
        return now() + timedelta(seconds=15)

    def register(self):
        """
        Заново заходит в игру, это нужно для появления ежедневных задач в событиях.
        """
        self.log(f'🎫 *{self.user.name}* заново заходит в игру…')
        self.api.prepare(invalidate_session=True)
        self.api.register()
        self.user = self.api.get_user_info()
        self.log(f'🎫 *{self.user.name}* заново зашел в игру.')

    def farm_daily_bonus(self):
        """
        Забирает ежедневный подарок.
        """
        self.log(f'*{self.user.name}* забирает ежедневный подарок…')
        with self.logger:
            self.logger.append(f'🎁 *{self.user.name}* получил в ежедневном подарке:', '')
            self.api.farm_daily_bonus().log(self.logger)

    def farm_expeditions(self) -> Optional[datetime]:
        """
        Собирает награду с экспедиций в дирижабле.
        """
        now_ = now()

        self.log(f'⛺️ *{self.user.name}* проверяет отправленные экспедиции…')
        expeditions = self.api.list_expeditions()
        for i, expedition in enumerate(expeditions, 1):
            if expedition.is_started and expedition.end_time < now_:
                with self.logger:
                    self.logger.append(f'⛺️ *{self.user.name}* получает награду с экспедиции:', '')
                    self.api.farm_expedition(expedition.id).log(self.logger)

        self.log(f'⛺️ *{self.user.name}* проверил отправленные экспедиции.')
        return self.send_expeditions()  # send expeditions once finished

    def send_expeditions(self) -> Optional[datetime]:
        logger.info('Sending expeditions…')
        self.log(f'⛺️ *{self.user.name}* пробует отправить экспедиции…')

        # Need to know which expeditions are already started.
        expeditions = self.api.list_expeditions()
        started_expeditions = [expedition for expedition in expeditions if expedition.is_started]
        logger.info('{} expeditions in progress.', len(started_expeditions))
        next_run_at = min([expedition.end_time for expedition in started_expeditions], default=None)
        if next_run_at:
            logger.info('The earliest expedition finishes at {}.', next_run_at.astimezone(self.user.tz))

        # Select available heroes.
        busy_ids = {hero_id for expedition in started_expeditions for hero_id in expedition.hero_ids}
        logger.info('Busy heroes: {}.', busy_ids)
        heroes: Dict[str, Hero] = {hero.id: hero for hero in self.api.get_all_heroes() if hero.id not in busy_ids}
        logger.info('{} heroes are still available.', len(heroes))

        # Let's see which expeditions are available.
        available_expeditions = [expedition for expedition in expeditions if expedition.is_available]
        logger.info('{} expeditions are still available.', len(available_expeditions))

        while available_expeditions:
            # Choose the least powerful expedition.
            expedition, *available_expeditions = sorted(available_expeditions, key=attrgetter('power'))
            logger.info('The optimal expedition power is {}.', expedition.power)

            # Choose the least powerful appropriate team.
            team = find_expedition_team(heroes.values(), expedition.power)
            if team is None:
                logger.info('Could not find powerful enough team.')
                break

            # Send the expedition.
            end_time, quests = self.api.send_expedition_heroes(expedition.id, get_unit_ids(team))
            self.log(f'⛺️ *{self.user.name}* отправил экспедицию #{expedition.id}.')
            self.farm_quests(quests)

            # Exclude the busy heroes.
            for hero in team:
                del heroes[hero.id]

            # We should farm the earliest finished expedition.
            if next_run_at is None or end_time < next_run_at:
                next_run_at = end_time

        self.log(f'⛺️ *{self.user.name}* закончил с отправкой экспедиций.')
        return next_run_at

    def farm_quests(self, quests: List[Quest] = None):
        """
        Собирает награды из заданий.
        """
        if quests is not None and not quests:
            logger.info('No quests to farm.')  # provided but empty
            return

        logger.info('Farming quests…')
        self.log(f'✅ *{self.user.name}* выполняет задачи…')
        if quests is None:
            quests = self.api.get_all_quests()
        for quest in quests:
            if not quest.is_reward_available:
                continue
            if self.settings.bot.no_experience and quest.reward.experience:
                logger.warning(f'Ignoring {quest.reward.experience} experience reward for quest #{quest.id}.')
                continue
            with self.logger:
                self.logger.append(f'✅ *{self.user.name}* получает за задачу:', '')
                self.api.farm_quest(quest.id).log(self.logger)
        self.log(f'✅ *{self.user.name}* выполнил задачи.')

    def farm_mail(self):
        """
        Собирает награды из почты.
        """
        logger.info('Farming mail…')
        self.log(f'📩 *{self.user.name}* читает почту…')
        letters = self.api.get_all_mail()
        if letters:
            logger.info(f'{len(letters)} letters.')
            with self.logger:
                self.logger.append(f'📩 *{self.user.name}* получил из почты:\n')
                log_rewards(self.api.farm_mail(letter.id for letter in letters).values(), self.logger)
        self.log(f'📩 *{self.user.name}* прочитал почту.')

    def buy_chest(self):
        """
        Открывает ежедневный бесплатный сундук.
        """
        self.log(f'🎁 *{self.user.name}* открывает сундук…')
        with self.logger:
            self.logger.append(f'🎁 *{self.user.name}* получил из сундука:', '')
            log_rewards(self.api.buy_chest(), self.logger)

    def send_daily_gift(self):
        """
        Отправляет сердечки друзьям.
        """
        self.log(f'❤️ *{self.user.name}* дарит сердечки друзьям…')
        if self.settings.bot.friend_ids:
            self.farm_quests(self.api.send_daily_gift(self.settings.bot.friend_ids))
        else:
            logger.warning('No friends specified.')
        self.log(f'❤️ *{self.user.name}* подарил сердечки друзьям.')

    def train_arena_model(self):
        """
        Тренирует предсказательную модель для арены.
        """
        self.log(f'🎲️ *{self.user.name}* тренирует модель…')
        Trainer(
            self.db,
            n_splits=constants.MODEL_N_SPLITS,
            n_last_battles=self.settings.bot.arena.last_battles,
        ).train()
        self.log(f'🎲️ *{self.user.name}* натренировал модель.')

    def attack_any_arena(
        self,
        *,
        n_heroes: int,
        make_solver: Callable[[Model, List[Hero]], ArenaSolver],
        attack: Callable[[ArenaSolution], Tuple[ArenaResult, Quests]],
        finalise: Callable[[], Any],
    ):
        self.log(f'⚔️ *{self.user.name}* идет на арену…')

        # Load arena model.
        logger.info('Loading model…')
        try:
            model: Model = pickle.loads(b85decode(self.db['bot:model']))
        except KeyError:
            logger.warning('Model is not ready yet.')
            return
        logger.trace('Model: {}.', model)

        # Get all heroes.
        heroes = self.api.get_all_heroes()
        if len(heroes) < n_heroes:
            logger.warning('Not enough heroes: {} needed, you have {}.', n_heroes, len(heroes))
            return

        # Refresh clan ID.
        self.user = self.api.get_user_info()

        # Pick an enemy and select attackers.
        solution = make_solver(model, heroes).solve()
        with self.logger:
            self.logger.append(f'⚔️ *{self.user.name}* атакует арену:', '')
            solution.log(self.logger)

        # Retry if win probability is too low.
        if solution.probability < constants.ARENA_MIN_PROBABILITY:
            logger.warning('Win probability is too low.')
            self.log(f'⚔️ *{self.user.name}* отменил атаку.')
            return now() + constants.ARENA_RETRY_INTERVAL

        # Attack!
        result, quests = attack(solution)

        # Collect results.
        with self.logger:
            self.logger.append(f'⚔️ *{self.user.name}* закончил арену:\n')
            result.log(self.logger)
        finalise()
        self.farm_quests(quests)

    def attack_normal_arena(self):
        """
        Совершает бой на обычной арене.
        """
        return self.attack_any_arena(
            n_heroes=constants.TEAM_SIZE,
            make_solver=lambda model, heroes: ArenaSolver(
                db=self.db,
                model=model,
                user_clan_id=self.user.clan_id,
                heroes=heroes,
                n_required_teams=1,
                max_iterations=self.settings.bot.arena.normal_max_pages,
                n_keep_solutions=self.settings.bot.arena.normal_keep_solutions,
                n_generate_solutions=self.settings.bot.arena.normal_generate_solutions,
                n_generations_count_down=self.settings.bot.arena.normal_generations_count_down,
                early_stop=self.settings.bot.arena.early_stop,
                get_enemies=self.api.find_arena_enemies,
                friendly_clans=self.settings.bot.arena.friendly_clans,
                reduce_probabilities=reduce_normal_arena,
                callback=lambda i: self.log(f'⚔️ *{self.user.name}* на странице *{i}* обычной арены…'),
            ),
            attack=lambda solution: self.api.attack_arena(solution.enemy.user_id, get_unit_ids(solution.attackers[0])),
            finalise=lambda: None,
        )

    def attack_grand_arena(self):
        """
        Совершает бой на гранд арене.
        """

        return self.attack_any_arena(
            n_heroes=constants.N_GRAND_HEROES,
            make_solver=lambda model, heroes: ArenaSolver(
                db=self.db,
                model=model,
                user_clan_id=self.user.clan_id,
                heroes=heroes,
                n_required_teams=constants.N_GRAND_TEAMS,
                max_iterations=self.settings.bot.arena.grand_max_pages,
                n_keep_solutions=self.settings.bot.arena.grand_keep_solutions,
                n_generate_solutions=self.settings.bot.arena.grand_generate_solutions,
                n_generations_count_down=self.settings.bot.arena.grand_generations_count_down,
                early_stop=self.settings.bot.arena.early_stop,
                get_enemies=self.api.find_grand_enemies,
                friendly_clans=self.settings.bot.arena.friendly_clans,
                reduce_probabilities=reduce_grand_arena,
                callback=lambda i: self.log(f'⚔️ *{self.user.name}* на странице *{i}* гранд-арены…'),
            ),
            attack=lambda solution: self.api.attack_grand(
                solution.enemy.user_id, get_teams_unit_ids(solution.attackers)),
            finalise=lambda: self.api.farm_grand_coins().log(),
        )

    def get_arena_replays(self):
        """
        Читает и сохраняет журналы арен.
        """
        self.log(f'📒️ *{self.user.name}* читает журнал арены…')

        replays: List[Replay] = [
            *self.api.get_battle_by_type(BattleType.ARENA),
            *self.api.get_battle_by_type(BattleType.GRAND),
        ]
        for replay in replays:
            if f'replays:{replay.id}' in self.db:
                continue
            self.db[f'replays:{replay.id}'] = {
                'start_time': replay.start_time.timestamp(),
                'win': replay.result.win,
                'attackers': [hero.dict() for hero in replay.attackers.values()],
                'defenders': [hero.dict() for defenders in replay.defenders for hero in defenders.values()],
            }
            logger.info(f'Saved #{replay.id}.')

        self.log(f'📒️ *{self.user.name}* прочитал журнал арены.')

    def check_freebie(self):
        """
        Собирает подарки на странице игры ВКонтакте.
        """
        self.log(f'🎁 *{self.user.name}* проверяет подарки на VK.com…')
        should_farm_mail = False

        for gift_id in self.vk.find_gifts():
            if f'gifts:{self.api.user_id}:{gift_id}' in self.db:
                continue
            logger.info(f'Checking {gift_id}…')
            reward = self.api.check_freebie(gift_id)
            if reward is not None:
                reward.log()
                should_farm_mail = True
            self.db[f'gifts:{self.api.user_id}:{gift_id}'] = True

        self.log(f'🎁 *{self.user.name}* проверил подарки на VK.com.')

        if should_farm_mail:
            self.farm_mail()

    def farm_zeppelin_gift(self):
        """
        Собирает ключ у валькирии и открывает артефактные сундуки.
        """
        self.log(f'🔑 *{self.user.name}* открывает артефактные сундуки…')

        self.api.farm_zeppelin_gift().log()
        for _ in range(constants.MAX_OPEN_ARTIFACT_CHESTS):
            try:
                rewards = self.api.open_artifact_chest()
            except NotEnoughError:
                logger.info('All keys are spent.')
                break
            with self.logger:
                self.logger.append(f'🔑 *{self.user.name}* получил из артефактного сундука:', '')
                log_rewards(rewards, self.logger)
        else:
            logger.warning('Maximum number of chests opened.')

        self.log(f'🔑 *{self.user.name}* открыл артефактные сундуки.')

    def raid_missions(self):
        """
        Ходит в рейды в миссиях в кампании за предметами.
        """
        self.log(f'🔥 *{self.user.name}* идет в рейды…')

        for mission_id in self.get_raid_mission_ids():
            logger.info(f'Raid mission #{mission_id} «{mission_name(mission_id)}»…')
            try:
                with self.logger:
                    rewards = self.api.raid_mission(mission_id)
                    self.logger.append(f'🔥 *{self.user.name}* получил из рейда «{mission_name(mission_id)}»:', '')
                    log_rewards(rewards, self.logger)
            except NotEnoughError as e:
                logger.info(f'Not enough: {e}.')
                break

        self.log(f'🔥 *{self.user.name}* сходил в рейды.')

    def shop(self):
        """
        Покупает в магазине вещи.
        """
        self.log(f'🛍 *{self.user.name}* идет в магазин…')

        logger.info(f'Requesting shops…')
        slots: List[Tuple[str, str]] = [
            (shop_id, slot.id)
            for shop_id in constants.SHOP_IDS
            for slot in self.api.get_shop(shop_id)
            if (not slot.is_bought) and (not slot.cost.star_money) and (slot.reward.keywords & self.settings.bot.shops)
        ]

        logger.info(f'Going to buy {len(slots)} slots.')
        for shop_id, slot_id in slots:
            logger.info(f'Buying slot #{slot_id} in shop «{shop_name(shop_id)}»…')
            try:
                reward = self.api.shop(shop_id=shop_id, slot_id=slot_id)
            except NotEnoughError as e:
                logger.warning(f'Not enough: {e}')
            except AlreadyError as e:
                logger.warning(f'Already: {e}')
            else:
                with self.logger:
                    self.logger.append(f'🛍 *{self.user.name}* купил:', '')
                    reward.log(self.logger)

        self.log(f'🛍 *{self.user.name}* сходил в магазин.')

    def skip_tower(self):
        """
        Зачистка башни.
        """
        self.log(f'🗼 *{self.user.name}* проходит башню…')

        tower = self.api.get_tower_info()
        heroes: List[str] = []

        # Yeah, it's a bit complicated…
        while tower.floor_number <= 50:
            logger.info(f'Floor #{tower.floor_number}: {tower.floor_type}.')
            self.log(f'🗼 *{self.user.name}* на {tower.floor_number}-м этаже башни…')

            if tower.floor_type == TowerFloorType.BATTLE:
                # If we have the top level, then we can skip the tower entirely.
                # But we need to go chest by chest. So go to the next chest.
                if tower.may_full_skip:
                    tower = self.api.next_tower_chest()
                # Maybe we can skip the floor, because of the yesterday progress.
                elif tower.floor_number <= tower.may_skip_floor:
                    tower, reward = self.api.skip_tower_floor()
                    reward.log()
                # Otherwise, we have to simulate the battle.
                else:
                    # Fetch the most powerful team, unless already done.
                    heroes = heroes or get_unit_ids(naive_select_attackers(self.api.get_all_heroes()))
                    try:
                        reward: Reward = execute_battle_with_retry(
                            mode=HeroesJSMode.TOWER,
                            start_battle=lambda: self.api.start_tower_battle(heroes),
                            end_battle=lambda response: self.api.end_tower_battle(response),
                        )
                    except NotEnoughStars:
                        # No attempt was successful, stop the tower.
                        logger.warning('Tower is stopped prematurely.')
                        break
                    else:
                        with self.logger:
                            self.logger.append(f'🗼 *{self.user.name}* получил на {tower.floor_number}-м этаже:\n')
                            reward.log(self.logger)
                        tower = self.api.next_tower_floor()
            elif tower.floor_type == TowerFloorType.CHEST:
                # The simplest one. Just open a random chest.
                reward, _ = self.api.open_tower_chest(choice([0, 1, 2]))
                with self.logger:
                    self.logger.append(f'🗼 *{self.user.name}* получил на {tower.floor_number}-м этаже башни:\n')
                    reward.log(self.logger)
                # If it was the top floor, we have to stop.
                if tower.floor_number == 50:
                    logger.success('Finished. It was the top floor.')
                    break
                # If we can skip the tower entirely, then go to the next chest.
                if tower.may_full_skip:
                    tower = self.api.next_tower_chest()
                # Otherwise, just proceed to the next floor.
                else:
                    tower = self.api.next_tower_floor()
            elif tower.floor_type == TowerFloorType.BUFF:
                # Buffs go from the cheapest to the most expensive.
                # So try to buy the most expensive ones first.
                for buff in reversed(tower.floor):
                    buff_id = int(buff['id'])
                    # Some buffs require to choose a hero. We ignore these.
                    if buff_id not in constants.TOWER_IGNORED_BUFF_IDS:
                        try:
                            self.api.buy_tower_buff(buff_id)
                        except NotEnoughError:
                            logger.info(f'Not enough resources for buff #{buff_id}.')
                        except AlreadyError:
                            logger.info(f'Already bought buff #{buff_id}.')
                        except NotFoundError as e:
                            logger.warning(f'Not found for buff #{buff_id}: {e}.')
                    else:
                        logger.debug(f'Skip buff #{buff_id}.')
                # Then normally proceed to the next floor.
                tower = self.api.next_tower_floor()

        self.log(f'🗼 *{self.user.name}* закончил башню на *{tower.floor_number}-м* этаже.')

    def farm_offers(self):
        """
        Фармит предложения (камни обликов).
        """
        self.log(f'🔵 *{self.user.name}* фармит предложения…')

        for offer in self.api.get_all_offers():
            logger.debug(f'#{offer.id}: {offer.offer_type}.')
            if offer.offer_type in constants.OFFER_FARMED_TYPES and not offer.is_free_reward_obtained:
                with self.logger:
                    self.logger.append(f'🔵 *{self.user.name}* получил за предложение:', '')
                    self.api.farm_offer_reward(offer.id).log(self.logger)

        self.log(f'🔵 *{self.user.name}* закончил фармить предложения.')

    def raid_bosses(self):
        """
        Рейдит боссов Запределья.
        """
        self.log(f'🔴 *{self.user.name}* рейдит боссов Запределья…')

        for i, boss in enumerate(self.api.get_all_bosses(), 1):
            self.log(f'🔴 *{self.user.name}* рейдит боссов Запределья: {i}-й…')
            if boss.may_raid:
                logger.info(f'Raid boss #{boss.id}…')
                self.api.raid_boss(boss.id).log()
                rewards, quests = self.api.open_boss_chest(boss.id)
                with self.logger:
                    self.logger.append(f'🔴 *{self.user.name}* получил в Запределье:', '')
                    log_rewards(rewards, self.logger)
                self.farm_quests(quests)
            else:
                logger.info(f'May not raid boss #{boss.id}.')

        self.log(f'🔴 *{self.user.name}* закончил рейд боссов Запределья.')

    def open_titan_artifact_chest(self):
        """
        Открывает сферы артефактов титанов.
        """
        self.log(f'⚫️ *{self.user.name}* открывает сферы артефактов титанов…')

        for amount in [10, 1]:
            try:
                rewards, quests = self.api.open_titan_artifact_chest(amount)
            except NotEnoughError:
                logger.info(f'Not enough resources to open {amount} chests.')
            else:
                with self.logger:
                    self.logger.append(f'⚫️ *{self.user.name}* получил из сферы артефактов титанов:', '')
                    log_rewards(rewards, self.logger)
                self.farm_quests(quests)
                break

        self.log(f'⚫️ *{self.user.name}* открыл сферы артефактов титанов.')

    def randomize_grand_defenders(self):
        """
        Выставляет в защиту гранд-арены топ-15 героев в случайном порядке.
        """
        self.log(f'🎲️ *{self.user.name}* изменяет защитников арены…')

        heroes = naive_select_attackers(self.api.get_all_heroes(), count=constants.N_GRAND_HEROES)
        if len(heroes) < constants.N_GRAND_HEROES:
            return
        hero_ids = get_unit_ids(heroes)
        shuffle(hero_ids)
        self.api.set_grand_heroes([hero_ids[0:5], hero_ids[5:10], hero_ids[10:15]])

        self.log(f'🎲️ *{self.user.name}* изменил защитников арены.')

    def enchant_rune(self):
        """
        Зачаровать руну.
        """
        self.log(f'🕉 *{self.user.name}* зачаровывает руну…')

        result = self.api.enchant_hero_rune(
            self.settings.bot.enchant_rune.hero_id,
            self.settings.bot.enchant_rune.tier,
        )
        logger.success('Response: {}.', result.response)
        self.log(f'🕉 *{self.user.name}* зачаровал руну.')

        self.farm_quests(result.quests)

    def level_up_titan_hero_gift(self):
        """
        Вложить и сбросить искры самому слабому герою.
        """
        self.log(f'⚡️ *{self.user.name}* вкладывает и сбрасывает искры мощи…')

        hero = min(self.api.get_all_heroes(), key=attrgetter('power'))
        logger.info('Hero: {}.', hero)
        self.farm_quests(self.api.level_up_titan_hero_gift(hero.id))
        reward, quests = self.api.drop_titan_hero_gift(hero.id)
        with self.logger:
            self.logger.append(f'⚡️ *{self.user.name}* получил за вложение искр мощи:', '')
            reward.log(self.logger)
        self.farm_quests(quests)

        self.log(f'⚡️ *{self.user.name}* вложил и сбросил искры мощи.')

    def clear_dungeon(self):
        """
        Подземелье.
        """
        self.log(f'🚇️ *{self.user.name}* идет в подземелье…')

        dungeon: Optional[Dungeon] = self.api.get_dungeon_info()

        # Prepare attacker lists.
        hero_ids = get_unit_ids(naive_select_attackers(self.api.get_all_heroes()))
        titans = self.api.get_all_titans()
        neutral_titan_ids = get_unit_ids(naive_select_attackers(titans))
        element_titan_ids = {
            element: get_unit_ids(naive_select_attackers(titan for titan in titans if titan.element == element))
            for element in LibraryTitanElement.__members__.values()
        }

        # Element (attacker type) usage counter. We'll try to use them evenly across titans.
        attacker_usage = Counter()

        # Clean the dungeon until the first save point.
        while dungeon is not None and not dungeon.floor.should_save_progress:
            logger.info('Floor: {}.', dungeon.floor_number)
            self.log(f'🚇️ *{self.user.name}* на *{dungeon.floor_number}-м* этаже подземелья…')
            team_number, user_data = min(
                enumerate(dungeon.floor.user_data),
                key=lambda item: attacker_usage[item[1].attacker_type],
            )
            logger.info('Using {}.', user_data.attacker_type)
            if user_data.attacker_type == DungeonUnitType.HERO:
                attacker_ids = hero_ids
                mode = HeroesJSMode.TOWER
            elif user_data.attacker_type == DungeonUnitType.NEUTRAL:
                attacker_ids = neutral_titan_ids
                mode = HeroesJSMode.TITAN
            else:
                attacker_usage[user_data.attacker_type] += 1
                logger.debug('Attacker usage: {}', attacker_usage)
                attacker_ids = element_titan_ids[constants.TITAN_ELEMENTS[user_data.attacker_type]]
                mode = HeroesJSMode.TITAN
            try:
                response: EndDungeonBattleResponse = execute_battle_with_retry(
                    mode=mode,
                    start_battle=lambda: self.api.start_dungeon_battle(attacker_ids, team_number),
                    end_battle=lambda response_: self.api.end_dungeon_battle(response_)
                )
            except NotEnoughStars:
                logger.warning('Dungeon is stopped prematurely.')
                break
            else:
                with self.logger:
                    self.logger.append(f'🚇️ *{self.user.name}* получил на *{dungeon.floor_number}-м* этаже:', '')
                    response.reward.log(self.logger)
                dungeon = response.dungeon

        # Save progress.
        if not dungeon or dungeon.floor.should_save_progress:
            self.log(f'🚇️ *{self.user.name}* сохраняется в подземелье…')
            response = self.api.save_dungeon_progress()
            with self.logger:
                self.logger.append(f'🚇️ *{self.user.name}* получил за сохранение:', '')
                response.reward.log(self.logger)
        else:
            logger.warning('Could not save the dungeon progress.')

        self.log(f'🚇️ *{self.user.name}* сходил в подземелье.')
        self.farm_quests()

    def hall_of_fame(self):
        """
        Турнир Стихий.
        """
        self.log(f'💨 *{self.user.name}* идет в Турнир Стихий…')

        weekday = now().weekday()

        if weekday == SATURDAY:
            logger.info('Farming reward today…')
            hall_of_fame = self.api.get_hall_of_fame()
            reward = self.api.farm_hall_of_fame_trophy_reward(hall_of_fame.trophy.week)
            with self.logger:
                self.logger.append(f'💨 *{self.user.name}* получил в Турнире Стихий:\n')
                reward.log(self.logger)
        else:
            logger.info('Doing nothing today.')

        self.log(f'💨 *{self.user.name}* закончил Турнир Стихий.')
