"""
Arena hero selection logic.
"""

import math
from abc import ABC, abstractmethod
from functools import lru_cache
from itertools import chain, combinations, permutations
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
        (enemy, attackers, probability), _ = secretary_max(
            self.iterate_enemies_pages(),
            self.max_iterations,
            key=self.probability_getter,
            early_stop=constants.ARENA_EARLY_STOP,
        )
        return enemy, attackers, probability

    def iterate_enemies_pages(self) -> Iterable[Tuple[TEnemy, TAttackers, float]]:
        while True:
            yield max(self.iterate_enemies(self.get_enemies_page()), key=self.probability_getter)

    def iterate_enemies(self, enemies: Iterable[TEnemy]) -> Tuple[TEnemy, TAttackers, float]:
        for enemy in enemies:
            if enemy.user is not None and not enemy.user.is_from_clan(self.user_clan_id):
                yield (enemy, *self.select_attackers(enemy))

    @abstractmethod
    def select_attackers(self, enemy: TEnemy) -> Tuple[TAttackers, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_iterations(self):
        raise NotImplementedError

    def _select_attackers(self, heroes: List[Hero], defenders: List[Hero], verbose=True) -> Tuple[List[Hero], float]:
        """
        Select attackers for the given enemy to maximise win probability.
        """

        hero_combinations_ = hero_combinations(len(heroes))

        # Select top N candidates by team power.
        selected_combinations: numpy.ndarray = numpy \
            .array([hero.power for hero in heroes])[hero_combinations_] \
            .sum(axis=1) \
            .argpartition(-constants.ARENA_COMBINATIONS_LIMIT)[-constants.ARENA_COMBINATIONS_LIMIT:]
        hero_combinations_ = hero_combinations_[selected_combinations]

        # Construct features.
        hero_features: numpy.ndarray = numpy.vstack(hero.get_features(self.model) for hero in heroes)
        defender_features: numpy.ndarray = numpy.vstack(hero.get_features(self.model) for hero in defenders)
        x: numpy.ndarray = hero_features[hero_combinations_].sum(axis=1) - defender_features.sum(axis=0)

        # Select top combination by win probability.
        y: numpy.ndarray = self.model.estimator.predict_proba(x)[:, 1]
        index: int = y.argmax()
        if verbose:
            logger.debug(f'👊 Win probability: {100.0 * y[index]:.1f}%.')
        return [heroes[i] for i in hero_combinations_[index]], y[index]


class Arena(AbstractArena[ArenaEnemy, List[Hero]]):
    @property
    def max_iterations(self):
        return constants.ARENA_MAX_ITERATIONS

    def select_attackers(self, enemy: ArenaEnemy) -> Tuple[List[Hero], float]:
        return self._select_attackers(self.heroes, enemy.heroes)


class GrandArena(AbstractArena[GrandArenaEnemy, List[List[Hero]]]):
    @property
    def max_iterations(self):
        return constants.GRAND_ARENA_MAX_ITERATIONS

    def select_attackers(self, enemy: GrandArenaEnemy) -> Tuple[List[List[Hero]], float]:
        """
        Select 3 teams of attackers for the given enemy to maximise win probability.
        It's not giving the best solution but it's fast enough.
        """
        selections: List[Tuple[List[List[Hero]], float, float, float, float]] = []

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
            selections.append((attackers_teams, probability, p1, p2, p3))

        # Choose best selection.
        attackers_teams, probability, p1, p2, p3 = max(selections, key=itemgetter(1))

        logger.debug(f'👊 Win probability: {100 * probability:.1f}% ({100 * p1:.1f}% {100 * p2:.1f}% {100 * p3:.1f}%).')
        return attackers_teams, probability


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def hero_combinations(hero_count: int) -> numpy.ndarray:
    """
    Used to generate indexes of possible heroes in a team.
    It it cached because hero count rarely changes.
    """
    return numpy.fromiter(chain.from_iterable(combinations(range(hero_count), constants.TEAM_SIZE)), dtype=int).reshape(-1, constants.TEAM_SIZE)


def secretary_max(items: Iterable[T1], n: int, key: Optional[Callable[[T1], T2]] = None, early_stop: T2 = None) -> Tuple[T1, T2]:
    """
    Select best item while lazily iterating over the items.
    https://en.wikipedia.org/wiki/Secretary_problem#Deriving_the_optimal_policy
    """
    r = int(n / math.e) + 1

    max_key = None

    for i, item in enumerate(items, start=1):
        item_key = key(item) if key else item
        # Check early stop condition.
        if early_stop is not None and item_key >= early_stop:
            return item, item_key
        # If it's the last item, just return it.
        if i == n:
            return item, item_key
        # Otherwise, check if the item is better than previous ones.
        if max_key is None or item_key > max_key:
            if i >= r:
                # Better than (r - 1) previous ones, return it.
                return item, item_key
            # Otherwise, update the best key.
            max_key = item_key

    raise RuntimeError('unreachable code')
