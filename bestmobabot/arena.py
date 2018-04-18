"""
Arena hero selection logic.
"""

import math
from abc import ABC, abstractmethod
from functools import reduce
from itertools import combinations, permutations
from operator import itemgetter
from typing import Callable, Generic, Iterable, List, Tuple, Optional, TypeVar

import numpy

from bestmobabot import constants
from bestmobabot.logger import logger
from bestmobabot.model import Model
from bestmobabot.responses import ArenaEnemy, GrandArenaEnemy, Hero

T = TypeVar('T')
T1 = TypeVar('T1')
T2 = TypeVar('T2')


# Enemy selection.
# ----------------------------------------------------------------------------------------------------------------------

TEnemy = TypeVar('TEnemy', ArenaEnemy, GrandArenaEnemy)
TAttackers = TypeVar('TAttackers')


class AbstractArena(ABC, Generic[TEnemy, TAttackers]):
    probability_getter = itemgetter(2)

    def __init__(
        self,
        model: Model,
        user_clan_id: Optional[str],
        heroes: List[Hero],
        get_enemies_page: Callable[[], List[TEnemy]],
    ):
        self.model = model
        self.user_clan_id = user_clan_id
        self.heroes = heroes
        self.get_enemies_page = get_enemies_page

    def select_enemy(self) -> Tuple[TEnemy, TAttackers, float]:
        self.set_heroes_model(self.heroes)
        (enemy, attackers, probability), _ = secretary_max(
            self.iterate_enemies_pages(), self.max_iterations, key=self.probability_getter, early_stop=0.99)
        return enemy, attackers, probability

    def iterate_enemies_pages(self) -> Iterable[Tuple[TEnemy, TAttackers, float]]:
        while True:
            yield max(self.iterate_enemies(self.get_enemies_page()), key=self.probability_getter)

    def iterate_enemies(self, enemies: Iterable[TEnemy]) -> Tuple[TEnemy, TAttackers, float]:
        for enemy in enemies:
            if enemy.user is not None and not enemy.user.is_from_clan(self.user_clan_id):
                yield (enemy, *self.select_attackers(enemy))

    def set_heroes_model(self, heroes: Iterable[Hero]):
        """
        Initialize heroes features.
        """
        for hero in heroes:
            hero.set_model(self.model)

    @staticmethod
    def make_team_features(heroes: Iterable[Hero]) -> numpy.ndarray:
        """
        Build model features for the specified heroes.
        """
        # noinspection PyTypeChecker
        return reduce(numpy.add, (hero.features for hero in heroes))

    @abstractmethod
    def select_attackers(self, enemy: TEnemy) -> Tuple[TAttackers, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_iterations(self):
        raise NotImplementedError

    def _select_attackers(self, heroes: List[Hero], defenders: List[Hero], verbose=True):
        """
        Select attackers for the given enemy to maximise win probability.
        """
        attackers_list = [list(attackers) for attackers in combinations(heroes, constants.TEAM_SIZE)]
        x = numpy.array([self.make_team_features(attackers) for attackers in attackers_list]) - self.make_team_features(defenders)
        y: numpy.ndarray = self.model.estimator.predict_proba(x)[:, 1]
        index: int = y.argmax()
        if verbose:
            logger.debug(f'👊 Win probability: {100.0 * y[index]:.1f}%.')
        return attackers_list[index], y[index]


class Arena(AbstractArena[ArenaEnemy, List[Hero]]):
    @property
    def max_iterations(self):
        return constants.MAX_ARENA_ITERATIONS

    def select_attackers(self, enemy: ArenaEnemy) -> Tuple[List[Hero], float]:
        self.set_heroes_model(enemy.heroes)
        return self._select_attackers(self.heroes, enemy.heroes)


class GrandArena(AbstractArena[GrandArenaEnemy, List[List[Hero]]]):
    @property
    def max_iterations(self):
        return constants.MAX_GRAND_ARENA_ITERATIONS

    def select_attackers(self, enemy: GrandArenaEnemy) -> Tuple[List[List[Hero]], float]:
        """
        Select 3 teams of attackers for the given enemy to maximise win probability.
        It's not giving the best solution but it's fast enough.
        """
        for heroes in enemy.heroes:
            self.set_heroes_model(heroes)

        selections: List[Tuple[List[List[Hero]], float]] = []

        # Try to form attackers teams in different order and maximise the final probability.
        for order in permutations(range(constants.GRAND_TEAMS)):
            used_heroes = set()
            attackers_teams: List[List[Hero]] = [[], [], []]
            probabilities: List[float] = [0.0, 0.0, 0.0]
            for i in order:
                heroes_left = [hero for hero in self.heroes if hero.id not in used_heroes]
                attackers, probabilities[i] = self._select_attackers(heroes_left, enemy.heroes[i], verbose=False)
                attackers_teams[i] = attackers
                used_heroes.update(attacker.id for attacker in attackers)
            p1, p2, p3 = probabilities
            probability = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)
            selections.append((attackers_teams, probability))

        # Choose best selection.
        attackers_teams, probability = max(selections, key=itemgetter(1))

        logger.debug(f'👊 Win probability: {100.0 * probability:.1f}%.')
        return attackers_teams, probability


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

def secretary_max(items: Iterable[T1], n: int, key: Optional[Callable[[T1], T2]] = None, early_stop: T2 = None) -> Tuple[T1, T2]:
    """
    Select best item while lazily iterating over the items.
    https://en.wikipedia.org/wiki/Secretary_problem#Deriving_the_optimal_policy
    """
    key = key or (lambda item: item)
    # We want to look at each item only once.
    iterator = iter((item, key(item)) for item in items)
    r = int(n / math.e) + 1
    # Skip first (r - 1) items and remember the maximum.
    _, max_key = max((next(iterator) for _ in range(r - 1)), key=itemgetter(1), default=(None, None))
    # Find the first one that is better or the last one.
    for item, item_key in iterator:  # type: T1, T2
        if max_key is None or item_key > max_key or (early_stop is not None and item_key > early_stop):
            break
    # noinspection PyUnboundLocalVariable
    return item, item_key
