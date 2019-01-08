"""
Arena hero selection logic.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from functools import lru_cache
from itertools import chain, combinations, count, product
from operator import itemgetter
from typing import Any, Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar

import numpy
from loguru import logger
# noinspection PyUnresolvedReferences
from numpy import arange, fromiter, ndarray, vstack
# noinspection PyUnresolvedReferences
from numpy.random import choice, permutation, randint

from bestmobabot.constants import GRAND_SIZE, TEAM_SIZE
from bestmobabot.dataclasses_ import ArenaEnemy, BaseArenaEnemy, GrandArenaEnemy, Hero, Team
from bestmobabot.itertools_ import CoolDown
from bestmobabot.model import Model
from bestmobabot.settings import Settings
from dataclasses import dataclass

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
        settings: Settings,
    ):
        self.model = model
        self.user_clan_id = user_clan_id
        self.heroes = heroes
        self.get_enemies_page = get_enemies_page
        self.settings = settings

        self.cache: Dict[str, Tuple[TAttackers, float]] = {}

    def select_enemy(self) -> Tuple[TEnemy, TAttackers, float]:
        return secretary_max(
            self.iterate_enemies_pages(),
            self.max_iterations,
            key=self.probability_getter,
            early_stop=self.settings.bot.arena.early_stop,
        )

    def iterate_enemies_pages(self) -> Iterable[Tuple[TEnemy, TAttackers, float]]:
        while True:
            enemies: List[Tuple[TEnemy, TAttackers, float]] = list(self.iterate_enemies(self.get_enemies_page()))
            # Yes, sometimes all enemies are filtered out.
            if enemies:
                yield max(enemies, key=self.probability_getter)

    def iterate_enemies(self, enemies: Iterable[TEnemy]) -> Tuple[TEnemy, TAttackers, float]:
        logger.info('Estimating win probability…')
        for enemy in enemies:
            if enemy.user is None:
                # Some enemies don't have user assigned. Filter them out.
                logger.debug(f'Skipped empty user.')
                continue
            if self.user_clan_id and enemy.user.is_from_clans((self.user_clan_id,)):
                logger.debug(f'Skipped same clan: «{enemy.user.name}».')
                continue
            if enemy.user.is_from_clans(self.settings.bot.arena.skip_clans):
                logger.debug(f'Skipped configured clan: «{enemy.user.clan_title}».')
                continue

            # It appears that often enemies are repeated during the search. So don't repeat computations.
            if enemy.user.id in self.cache:
                attackers, probability = self.cache[enemy.user.id]
                logger.info(f'«{enemy.user.name}» from «{enemy.user.clan_title}»: {100.0 * probability:.1f}% (cached)')
            else:
                attackers, probability = self.select_attackers(enemy)  # type: TAttackers, float
                self.cache[enemy.user.id] = attackers, probability
            yield (enemy, attackers, probability)

    def make_hero_features(self, hero: Hero) -> ndarray:
        """
        Make hero features 1D-array.
        """
        return fromiter((hero.features.get(name, 0.0) for name in self.model.feature_names), numpy.float)

    def make_team_features(self, heroes: Iterable[Hero]) -> ndarray:
        """
        Make team features 2D-array. Shape is number of heroes × number of features.
        """
        return vstack(self.make_hero_features(hero) for hero in heroes)

    @abstractmethod
    def select_attackers(self, enemy: TEnemy) -> Tuple[TAttackers, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_iterations(self):
        raise NotImplementedError


class Arena(AbstractArena[ArenaEnemy, List[Hero]]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_teams_limit = self.settings.bot.arena.teams_limit
        logger.info(f'Teams count limit: {self.n_teams_limit}.')

    @property
    def max_iterations(self):
        return self.settings.bot.arena.max_pages

    def select_attackers(self, enemy: ArenaEnemy) -> Tuple[List[Hero], float]:
        """
        Select attackers for the given enemy to maximise win probability.
        """

        hero_combinations_ = hero_combinations(len(self.heroes))

        # Select top N candidates by team power.
        selected_combinations: ndarray = numpy \
            .array([hero.power for hero in self.heroes])[hero_combinations_] \
            .sum(axis=1) \
            .argpartition(-self.n_teams_limit)[-self.n_teams_limit:]
        hero_combinations_ = hero_combinations_[selected_combinations]

        # Construct features.
        x: ndarray = (
            self.make_team_features(self.heroes)[hero_combinations_].sum(axis=1)
            - self.make_team_features(enemy.heroes).sum(axis=0)
        )

        # Select top combination by win probability.
        y: ndarray = self.model.estimator.predict_proba(x)[:, 1]
        index: int = y.argmax()
        logger.info(f'«{enemy.user.name}» from «{enemy.user.clan_title}»: {100.0 * y[index]:.1f}%')
        return [self.heroes[i] for i in hero_combinations_[index]], y[index]


class GrandArena(AbstractArena[GrandArenaEnemy, List[List[Hero]]]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n_generate_solutions = self.settings.bot.arena.grand_generate_solutions
        self.n_keep_solutions = self.settings.bot.arena.grand_keep_solutions

        # We keep solutions in an attribute because we want to retry the best solutions across different enemies.
        logger.trace('Generating initial solutions…')
        self.solutions: ndarray = vstack(
            permutation(len(self.heroes))
            for _ in range(self.n_keep_solutions)
        )

    @property
    def max_iterations(self):
        return self.settings.bot.arena.max_grand_pages

    def select_attackers(self, enemy: GrandArenaEnemy) -> Tuple[List[List[Hero]], float]:
        logger.trace(f'Selecting attackers for «{enemy.user.name}»…')

        n_heroes = len(self.heroes)
        hero_features = self.make_team_features(self.heroes)
        defenders_features = [self.make_team_features(heroes).sum(axis=0) for heroes in enemy.heroes]

        # Used to select separate teams from the population array.
        team_selectors = (slice(0, 5), slice(5, 10), slice(10, 15))

        # Possible permutations of a single solution.
        # Each permutation swaps two particular elements so that the heroes are moved to or from the teams.
        swaps = vstack(swap_permutation(n_heroes, i, j) for i, j in chain(
            product(range(0, 5), range(5, 10)),
            product(range(0, 5), range(10, 15)),
            product(range(5, 10), range(10, 15)),
            product(range(GRAND_SIZE), range(GRAND_SIZE, n_heroes)),
        ))

        # Let's evolve.
        max_index: int = None
        max_probability = 0.0
        cool_down = CoolDown(count(1), self.settings.bot.arena.grand_generations_cool_down)

        for n_generation in cool_down:
            # Generate new solutions.
            # Choose random solutions from the population and apply a random permutation to each of them.
            new_permutations = swaps[randint(0, swaps.shape[0], self.n_generate_solutions)]
            new_solutions = self.solutions[
                choice(self.solutions.shape[0], self.n_generate_solutions).reshape(-1, 1),
                new_permutations
            ]

            # Stack past solutions with the new ones.
            self.solutions = vstack((self.solutions, new_solutions))

            # Predict probabilities.
            # Call to `predict_proba` is expensive, thus call it for all the grand teams at once. Stack and split.
            x = vstack(
                hero_features[self.solutions[:, selector]].sum(axis=1) - defender_features
                for selector, defender_features in zip(team_selectors, defenders_features)
            )
            p1, p2, p3 = numpy.split(self.model.estimator.predict_proba(x)[:, 1], 3)
            probabilities = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)

            # Select top ones for the next iteration.
            # See also: https://stackoverflow.com/a/23734295/359730
            top_indexes = probabilities.argpartition(-self.n_keep_solutions)[-self.n_keep_solutions:]
            self.solutions = self.solutions[top_indexes, :]
            probabilities = probabilities[top_indexes]
            p1, p2, p3 = p1[top_indexes], p2[top_indexes], p3[top_indexes]

            # Select the best one.
            max_index = probabilities.argmax()
            if probabilities[max_index] - max_probability > 0.00001:
                # Improved solution. Give the optimizer another chance to beat the best solution.
                cool_down.reset()
            max_probability = probabilities[max_index]
            logger.trace(f'Generation {n_generation:2}: {100.0 * max_probability:.2f}%{" +" if cool_down.is_fresh else ""}')  # noqa

            # I'm feeling lucky!
            if max_probability > 0.99999:
                break

        # noinspection PyUnboundLocalVariable
        logger.info(
            f'«{enemy.user.name}» from «{enemy.user.clan_title}»:'
            f' {100.0 * max_probability:.2f}%'
            f' ({100 * p1[max_index]:.1f}% {100 * p2[max_index]:.1f}% {100 * p3[max_index]:.1f}%)'
        )

        return [
            [self.heroes[i] for i in self.solutions[max_index, selector]]
            for selector in team_selectors
        ], max_probability


# Universal arena solver.
# TODO: work in progress.
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class ArenaSolution:
    enemy: BaseArenaEnemy
    attackers: List[Team]
    probability: float

    def __lt__(self, other: ArenaSolution) -> Any:
        if isinstance(other, ArenaSolution):
            return self.probability < other.probability
        return NotImplemented


class ArenaSolver:
    """
    Generic arena solver for both normal arena and grand arena.
    """

    def __init__(
        self,
        *,
        model: Model,
        user_clan_id: Optional[str],
        heroes: List[Hero],
        max_iterations: int,
        n_keep_solutions: int,
        n_generate_solutions: int,
        n_generations_cool_down: int,
        early_stop: float,
        get_enemies: Callable[[], List[BaseArenaEnemy]],
        friendly_clans: Iterable[str],
        reduce_probabilities: Callable[[List[ndarray]], ndarray],
    ):
        """
        :param model: prediction model.
        :param user_clan_id: current user clan ID.
        :param heroes: current user heroes.
        :param max_iterations: maximum number of `get_enemies` calls.
        :param n_keep_solutions: number of the best kept solutions from each generation.
        :param n_generate_solutions: number of newly generated solutions in each generation.
        :param n_generations_cool_down: for how much generations should a solution stay the best.
        :param early_stop: minimal probability to attack the enemy immediately.
        :param get_enemies: callable to fetch an enemy page.
        :param friendly_clans: friendly clan IDs or titles.
        :param reduce_probabilities: callable to combine probabilities from multiple battles into a final one.
        """

        self.model = model
        self.user_clan_id = user_clan_id
        self.heroes = heroes
        self.max_iterations = max_iterations
        self.n_keep_solutions = n_keep_solutions
        self.n_generate_solutions = n_generate_solutions
        self.n_generations_cool_down = n_generations_cool_down
        self.early_stop = early_stop
        self.get_enemies = get_enemies
        self.friendly_clans = set(friendly_clans)
        self.reduce_probabilities = reduce_probabilities

        # If the same enemy is encountered again, we will use the earlier solution.
        self.cache: Dict[str, ArenaSolution] = {}

        # We keep solutions in an attribute because we want to retry the best solutions across different enemies.
        self.solutions = numpy.array([[]])

    def solve(self) -> ArenaSolution:
        logger.debug('Generating initial solutions…')
        self.solutions = vstack(permutation(len(self.heroes)) for _ in range(self.n_keep_solutions))
        return secretary_max(self.yield_solutions(), self.max_iterations, early_stop=self.early_stop)

    def yield_solutions(self) -> Iterable[ArenaSolution]:
        """
        Yield best solution from each `get_enemies` call.
        """
        while True:
            logger.debug('Fetching enemies…')
            enemies = list(self.filter_enemies(self.get_enemies()))
            if enemies:
                yield max(self.solve_enemy(enemy) for enemy in enemies)
            else:
                logger.debug('All enemies are filtered out on the current page.')

    def filter_enemies(self, enemies: Iterable[BaseArenaEnemy]) -> Iterable[BaseArenaEnemy]:
        """
        Filter out "bad" enemies and enemies from the friendly clans.
        """
        for enemy in enemies:
            if enemy.user is None:
                logger.debug('Skipped empty user #{}.', enemy.user_id)
                continue
            if self.user_clan_id and enemy.user.is_from_clans((self.user_clan_id,)):
                logger.info('Skipped enemy «{}» from your clan.', enemy.user.name)
                continue
            if enemy.user.is_from_clans(self.friendly_clans):
                logger.info('Skipped enemy «{user.name}» from «{user.clan_title}».', user=enemy.user)
                continue
            yield enemy

    def solve_enemy(self, enemy: BaseArenaEnemy) -> ArenaSolution:
        """
        Finds solution for the single enemy.
        """
        logger.debug('Solving arena for «{user.name}» from «{user.clan_title}»…', user=enemy.user)

        n_heroes = len(self.heroes)
        n_teams = len(enemy.teams)
        hero_features = self.make_team_features(self.heroes)
        defenders_features = [self.make_team_features(team).sum(axis=0) for team in enemy.teams]

        # Used to select separate teams from the population array.
        team_selectors = slices(n_teams, TEAM_SIZE)

        # Possible (per)mutations of a single solution.
        # Each permutation swaps two particular elements so that the heroes are replaced between the teams.
        swaps = vstack(swap_permutation(n_heroes, i, j) for i, j in chain(
            product(range(0, 5), range(5, 10)),
            product(range(0, 5), range(10, 15)),
            product(range(5, 10), range(10, 15)),
            product(range(GRAND_SIZE), range(GRAND_SIZE, n_heroes)),
        ))  # FIXME

        # Let's evolve.
        cool_down = CoolDown(count(1), self.n_generations_cool_down)
        ys: List[ndarray] = []
        max_index: int = None
        max_probability = 0.0

        for n_generation in cool_down:
            # Generate new solutions.
            # Choose random solutions from the population and apply a random permutation to each of them.
            new_permutations = swaps[randint(0, swaps.shape[0], self.n_generate_solutions)]
            new_solutions = self.solutions[
                choice(self.solutions.shape[0], self.n_generate_solutions).reshape(-1, 1),
                new_permutations
            ]

            # Stack old solutions with the new ones.
            self.solutions = vstack((self.solutions, new_solutions))

            # Predict probabilities.
            # Call to `predict_proba` is expensive, thus call it for all the teams at once. Stack and split.
            x = vstack(
                hero_features[self.solutions[:, selector]].sum(axis=1) - defender_features
                for selector, defender_features in zip(team_selectors, defenders_features)
            )
            ys = numpy.split(self.model.estimator.predict_proba(x)[:, 1], n_teams)
            probabilities = self.reduce_probabilities(ys)  # vector of reduced probabilities

            # Select top ones for the next iteration.
            # See also: https://stackoverflow.com/a/23734295/359730
            top_indexes = probabilities.argpartition(-self.n_keep_solutions)[-self.n_keep_solutions:]
            self.solutions = self.solutions[top_indexes, :]
            probabilities = probabilities[top_indexes]

            # Select the best one.
            max_index = probabilities.argmax()
            if probabilities[max_index] - max_probability > 0.00001:
                # Improved solution. Give the optimizer another chance to beat the best solution.
                cool_down.reset()
            max_probability = probabilities[max_index]
            logger.trace(
                'Generation {:2}: {:.2f}%{}',
                n_generation,
                100.0 * max_probability,
                (" +" if cool_down.is_fresh else ""),
            )

            # I'm feeling lucky!
            if max_probability > 0.99999:
                break

        logger.info(
            '«{}» from «{}»: {:.1f}% ({})',
            enemy.user.name,
            enemy.user.clan_title,
            100.0 * max_probability,
            ' '.join(f'{100 * y[max_index]:.1f}%' for y in ys),
        )

        return ArenaSolution(
            enemy=enemy,
            attackers=[
                [self.heroes[i] for i in self.solutions[max_index, selector]]
                for selector in team_selectors
            ],
            probability=max_probability,
        )

    def make_hero_features(self, hero: Hero) -> ndarray:
        """
        Make hero features 1D-array.
        """
        # noinspection PyUnresolvedReferences
        return numpy.fromiter((hero.features.get(name, 0.0) for name in self.model.feature_names), numpy.float)

    def make_team_features(self, team: Team) -> ndarray:
        """
        Make team features 2D-array. Shape is number of heroes × number of features.
        """
        return vstack(self.make_hero_features(hero) for hero in team)


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def hero_combinations(hero_count: int) -> ndarray:
    """
    Used to generate indexes of possible heroes in a team.
    It it cached because hero count rarely changes.
    """
    return fromiter(chain.from_iterable(combinations(range(hero_count), TEAM_SIZE)), dtype=int).reshape(-1, TEAM_SIZE)  # noqa


def swap_permutation(size: int, index_1: int, index_2: int) -> ndarray:
    permutation = arange(size)
    permutation[[index_1, index_2]] = permutation[[index_2, index_1]]
    return permutation


def ranges(n_ranges: int, range_size: int) -> Iterable[range]:
    return (range(i * range_size, (i + 1) * range_size) for i in range(n_ranges))


def slices(n_slices: int, slice_size: int) -> Tuple[slice, ...]:
    return tuple(slice(range_.start, range_.stop) for range_ in ranges(n_slices, slice_size))


def secretary_max(
    items: Iterable[T1],
    n: int,
    key: Optional[Callable[[T1], T2]] = None,
    early_stop: T2 = None,
) -> T1:
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
            return item
        # If it's the last item, just return it.
        if i == n:
            return item
        # Otherwise, check if the item is better than previous ones.
        if max_key is None or item_key >= max_key:
            if i >= r:
                # Better than (r - 1) previous ones, return it.
                return item
            # Otherwise, update the best key.
            max_key = item_key

    raise RuntimeError('unreachable code')
