"""
Arena hero selection logic.
"""

import math
from abc import ABC, abstractmethod
from functools import lru_cache
from itertools import chain, combinations, product
from operator import itemgetter
from typing import Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar

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
        *,
        model: Model,
        user_clan_id: Optional[str],
        heroes: List[Hero],
        get_enemies_page: Callable[[], List[TEnemy]],
        early_stop: float,
    ):
        self.model = model
        self.user_clan_id = user_clan_id
        self.heroes = heroes
        self.get_enemies_page = get_enemies_page
        self.arena_early_stop = early_stop

        self.cache: Dict[str, Tuple[TAttackers, float]] = {}

    def select_enemy(self) -> Tuple[TEnemy, TAttackers, float]:
        (enemy, attackers, probability), _ = secretary_max(
            self.iterate_enemies_pages(),
            self.max_iterations,
            key=self.probability_getter,
            early_stop=self.arena_early_stop,
        )
        return enemy, attackers, probability

    def iterate_enemies_pages(self) -> Iterable[Tuple[TEnemy, TAttackers, float]]:
        while True:
            enemies: List[Tuple[TEnemy, TAttackers, float]] = list(self.iterate_enemies(self.get_enemies_page()))
            # Yes, sometimes all enemies are filtered out.
            if enemies:
                yield max(enemies, key=self.probability_getter)

    def iterate_enemies(self, enemies: Iterable[TEnemy]) -> Tuple[TEnemy, TAttackers, float]:
        logger.info('🎲 Estimating win probability…')
        for enemy in enemies:
            # Some enemies don't have user assigned. Filter them out.
            if enemy.user is not None and not enemy.user.is_from_clan(self.user_clan_id):
                # It appears that often enemies are repeated during the search. So don't repeat computations.
                if enemy.user.id in self.cache:
                    attackers, probability = self.cache[enemy.user.id]
                    logger.info(f'🎲 Cached entry found: {100.0 * probability:.1f}% ("{enemy.user.name}").')
                else:
                    attackers, probability = self.select_attackers(enemy)  # type: TAttackers, float
                    self.cache[enemy.user.id] = attackers, probability
                yield (enemy, attackers, probability)

    def make_features(self, heroes: Iterable[Hero]) -> numpy.ndarray:
        """
        Make hero features array. Shape is number of heroes × number of features.
        """
        return numpy.vstack(hero.get_features(self.model) for hero in heroes)

    @abstractmethod
    def select_attackers(self, enemy: TEnemy) -> Tuple[TAttackers, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_iterations(self):
        raise NotImplementedError


class Arena(AbstractArena[ArenaEnemy, List[Hero]]):
    def __init__(self, n_teams_limit: int, **kwargs):
        super().__init__(**kwargs)
        self.n_teams_limit = n_teams_limit
        logger.info(f'🎲 Teams count limit: {n_teams_limit}.')

    @property
    def max_iterations(self):
        return constants.ARENA_MAX_PAGES

    def select_attackers(self, enemy: ArenaEnemy) -> Tuple[List[Hero], float]:
        """
        Select attackers for the given enemy to maximise win probability.
        """

        hero_combinations_ = hero_combinations(len(self.heroes))

        # Select top N candidates by team power.
        selected_combinations: numpy.ndarray = numpy \
            .array([hero.power for hero in self.heroes])[hero_combinations_] \
            .sum(axis=1) \
            .argpartition(-self.n_teams_limit)[-self.n_teams_limit:]
        hero_combinations_ = hero_combinations_[selected_combinations]

        # Construct features.
        x: numpy.ndarray = (
            self.make_features(self.heroes)[hero_combinations_].sum(axis=1)
            - self.make_features(enemy.heroes).sum(axis=0)
        )

        # Select top combination by win probability.
        y: numpy.ndarray = self.model.estimator.predict_proba(x)[:, 1]
        index: int = y.argmax()
        logger.info(f'🎲 Win probability: {100.0 * y[index]:.1f}% ("{enemy.user.name}").')
        return [self.heroes[i] for i in hero_combinations_[index]], y[index]


class GrandArena(AbstractArena[GrandArenaEnemy, List[List[Hero]]]):
    def __init__(self, *, n_generations: int, **kwargs):
        super().__init__(**kwargs)
        self.n_generations = n_generations
        logger.info(f'🎲 Generations count: {n_generations}.')

    @property
    def max_iterations(self):
        return constants.GRAND_ARENA_MAX_PAGES

    def select_attackers(self, enemy: GrandArenaEnemy) -> Tuple[List[List[Hero]], float]:
        n_heroes = len(self.heroes)
        hero_features = self.make_features(self.heroes)
        defenders_features = [self.make_features(heroes).sum(axis=0) for heroes in enemy.heroes]

        # Generate initial solutions.
        solutions: numpy.ndarray = numpy.vstack(numpy.random.permutation(n_heroes) for _ in range(constants.GRAND_ARENA_N_KEEP))

        # Used to select separate teams from the population array.
        team_selectors = (slice(0, 5), slice(5, 10), slice(10, 15))

        # Possible permutations of a single solution.
        # Each permutation swaps two particular elements so that the heroes are moved to or from the teams.
        swaps = numpy.vstack(swap_permutation(n_heroes, i, j) for i, j in chain(
            product(range(0, 5), range(5, 10)),
            product(range(0, 5), range(10, 15)),
            product(range(5, 10), range(10, 15)),
            product(range(constants.GRAND_SIZE), range(constants.GRAND_SIZE, n_heroes)),
        ))

        # Let's evolve.
        max_index: int = None
        max_probability = 0.0

        for n_generation in range(self.n_generations):
            # Generate new solutions.
            # Choose random solutions from the population and apply a random permutation to each of them.
            new_permutations = swaps[numpy.random.randint(0, swaps.shape[0], constants.GRAND_ARENA_N_GENERATE)]
            new_solutions = solutions[
                numpy.random.choice(solutions.shape[0], constants.GRAND_ARENA_N_GENERATE).reshape(-1, 1),
                new_permutations
            ]

            # Stack past solutions with the new ones.
            solutions = numpy.vstack((solutions, new_solutions))

            # Predict probabilities.
            # Call to `predict_proba` is expensive, thus call it for all the grand teams at once. Stack and split.
            x = numpy.vstack(
                hero_features[solutions[:, selector]].sum(axis=1) - defender_features
                for selector, defender_features in zip(team_selectors, defenders_features)
            )
            p1, p2, p3 = numpy.split(self.model.estimator.predict_proba(x)[:, 1], 3)
            probabilities = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)

            # Select top ones.
            top_indexes = probabilities.argpartition(-constants.GRAND_ARENA_N_KEEP)[-constants.GRAND_ARENA_N_KEEP:]
            solutions = solutions[top_indexes, :]
            probabilities = probabilities[top_indexes]

            # Select the best one.
            max_index = probabilities.argmax()
            max_probability = probabilities[max_index]

        logger.info(
            '🎲 Win probability:'
            f' {100.0 * max_probability:.2f}%'
            f' ({100 * p1[max_index]:.1f}% {100 * p2[max_index]:.1f}% {100 * p3[max_index]:.1f}%)'
            f' ("{enemy.user.name}")'
        )

        return [[self.heroes[i] for i in solutions[max_index, selector]] for selector in team_selectors], max_probability


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def hero_combinations(hero_count: int) -> numpy.ndarray:
    """
    Used to generate indexes of possible heroes in a team.
    It it cached because hero count rarely changes.
    """
    return numpy.fromiter(chain.from_iterable(combinations(range(hero_count), constants.TEAM_SIZE)), dtype=int).reshape(-1, constants.TEAM_SIZE)


def swap_permutation(size: int, index_1: int, index_2: int) -> numpy.ndarray:
    permutation = numpy.arange(size)
    permutation[[index_1, index_2]] = permutation[[index_2, index_1]]
    return permutation


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
