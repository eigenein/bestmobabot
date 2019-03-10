"""
Arena hero selection logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from itertools import combinations, count, product
from typing import Any, Callable, Dict, Iterable, List, MutableMapping, Optional, TypeVar

import numpy
from loguru import logger
# noinspection PyUnresolvedReferences
from numpy import arange, ndarray, vstack
# noinspection PyUnresolvedReferences
from numpy.random import choice, permutation, randint

from bestmobabot.constants import TEAM_SIZE
from bestmobabot.dataclasses_ import BaseArenaEnemy, Hero, Loggable
from bestmobabot.itertools_ import CountDown, secretary_max, slices
from bestmobabot.model import Model

T = TypeVar('T')


# Universal arena solver.
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
@total_ordering
class ArenaSolution(Loggable):
    enemy: BaseArenaEnemy  # selected enemy
    attackers: List[List[Hero]]  # player's attacker teams
    probability: float  # arena win probability
    probabilities: List[float]  # individual battle win probabilities

    @property
    def plain_text(self) -> Iterable[str]:
        yield 'Solution:'
        yield str(self)
        for i, (defenders, attackers) in enumerate(zip(self.enemy.teams, self.attackers), start=1):
            yield f'Defenders #{i}'
            for hero in sorted(defenders, reverse=True):
                yield str(hero)
            yield f'Attackers #{i}'
            for hero in sorted(attackers, reverse=True):
                yield str(hero)

    @property
    def markdown(self) -> Iterable[str]:
        yield f'*{self.enemy.user.name}* из клана *{self.enemy.user.clan_title}*'
        yield f'Место: *{self.enemy.place}*'
        yield ' '.join([
            f'Вероятность победы: *{100.0 * self.probability:.1f}%*',
            f'({" ".join(f"*{100 * probability:.1f}%*" for probability in self.probabilities)})',
        ])

    def __lt__(self, other: ArenaSolution) -> Any:
        if isinstance(other, ArenaSolution):
            return self.probability < other.probability
        if isinstance(other, float):
            return self.probability < other
        return NotImplemented

    def __str__(self):
        return (
            f'{self.enemy}: {100.0 * self.probability:.1f}%'
            f' ({" ".join(f"{100 * probability:.1f}%" for probability in self.probabilities)})'
        )


class ArenaSolver:
    """
    Generic arena solver for both normal arena and grand arena.
    """

    # TODO: maybe move parameters to a separate dataclass.
    def __init__(
        self,
        *,
        db: MutableMapping[str, Any],
        model: Model,
        user_clan_id: Optional[str],
        heroes: List[Hero],
        n_required_teams: int,
        max_iterations: int,
        n_keep_solutions: int,
        n_generate_solutions: int,
        n_generations_count_down: int,
        early_stop: float,
        get_enemies: Callable[[], List[BaseArenaEnemy]],
        friendly_clans: Iterable[str],
        reduce_probabilities: Callable[..., ndarray],
        callback: Callable[[int], Any],
    ):
        """
        :param model: prediction model.
        :param user_clan_id: current user clan ID.
        :param heroes: current user heroes.
        :param n_required_teams: how much teams must be generated.
        :param max_iterations: maximum number of `get_enemies` calls.
        :param n_keep_solutions: number of the best kept solutions from each generation.
        :param n_generate_solutions: number of newly generated solutions in each generation.
        :param n_generations_count_down: for how much generations should a solution stay the best.
        :param early_stop: minimal probability to attack the enemy immediately.
        :param get_enemies: callable to fetch an enemy page.
        :param friendly_clans: friendly clan IDs or titles.
        :param reduce_probabilities: callable to combine probabilities from multiple battles into a final one.
        :param callback: callable which receives current arena enemies page.
        """

        self.db = db
        self.model = model
        self.user_clan_id = user_clan_id
        self.heroes = heroes
        self.n_required_teams = n_required_teams
        self.max_iterations = max_iterations
        self.n_keep_solutions = n_keep_solutions
        self.n_generate_solutions = n_generate_solutions
        self.n_generations_count_down = n_generations_count_down
        self.early_stop = early_stop
        self.get_enemies = get_enemies
        self.friendly_clans = set(friendly_clans)
        self.reduce_probabilities = reduce_probabilities
        self.callback = callback

        # If the same enemy is encountered again, we will use the earlier solution.
        self.cache: Dict[str, ArenaSolution] = {}

        # We keep solutions in an attribute because we want to retry the best solutions across different enemies.
        self.solutions = numpy.array([[]])

    def solve(self) -> ArenaSolution:
        logger.debug('Generating initial solutions…')
        self.solutions = vstack([permutation(len(self.heroes)) for _ in range(self.n_keep_solutions)])
        return secretary_max(self.yield_solutions(), self.max_iterations, early_stop=self.early_stop)

    def yield_solutions(self) -> Iterable[ArenaSolution]:
        """
        Yield best solution from each `get_enemies` call.
        """
        for n_page in count(1):
            logger.debug('Fetching enemies…')
            self.callback(n_page)
            enemies = list(self.filter_enemies(self.get_enemies()))
            if enemies:
                yield max(self.solve_enemy_cached(enemy) for enemy in enemies)
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
            if len(enemy.teams) < self.n_required_teams:
                logger.warning('Enemy has unknown teams: {}.', enemy.user)
                continue
            self.store_enemy(enemy)
            if self.user_clan_id and enemy.user.is_from_clans((self.user_clan_id,)):
                logger.info('Skipped enemy «{}» from your clan.', enemy.user.name)
                continue
            if enemy.user.is_from_clans(self.friendly_clans):
                logger.info('Skipped enemy {}.', enemy.user)
                continue
            yield enemy

    def store_enemy(self, enemy: BaseArenaEnemy):
        """
        Store enemy teams and place to be able to guess their hidden teams in Top 100.
        """
        enemy_key = f'arena:{self.n_required_teams}:{enemy.user.server_id}:{enemy.user_id}'
        self.db[f'{enemy_key}:teams'] = [[hero.dict() for hero in team] for team in enemy.teams]
        self.db[f'{enemy_key}:place'] = enemy.place

    def solve_enemy_cached(self, enemy: BaseArenaEnemy) -> ArenaSolution:
        """
        Makes use of the solution cache for repeated enemies.
        """
        solution = self.cache.get(enemy.user_id)
        if not solution:
            solution = self.solve_enemy(enemy)
            self.cache[enemy.user_id] = solution
        else:
            logger.debug('Cache hit: #{}.', enemy.user_id)
        logger.success('{}', solution)
        return solution

    def solve_enemy(self, enemy: BaseArenaEnemy) -> ArenaSolution:
        """
        Finds solution for the single enemy.
        """
        logger.debug('Solving arena for {}…', enemy)

        n_heroes = len(self.heroes)
        n_actual_teams = len(enemy.teams)  # at first we will generate the same number of attacker teams
        n_attackers = n_actual_teams * TEAM_SIZE

        hero_features = self.make_team_features(self.heroes)
        defenders_features = [self.make_team_features(team).sum(axis=0) for team in enemy.teams]

        # Used to speed up selection of separate attacker teams from the solutions array.
        team_selectors = slices(n_actual_teams, TEAM_SIZE)

        # Generate all possible (per)mutations of a single solution.
        # We will use it to speed up mutation process by selecting random rows from the `swaps` array.
        # Each permutation swaps two particular elements so that the heroes are interchanged in the teams.
        # In total `n_teams + 1` groups.
        groups = [
            *[range(selector.start, selector.stop) for selector in team_selectors],
            range(n_attackers, n_heroes),  # fake group to keep unused heroes in
        ]
        logger.trace('{} hero groups.', len(groups))
        swaps = vstack([
            swap_permutation(n_heroes, i, j)  # swap these two heroes
            for group_1, group_2 in combinations(groups, 2)  # select two groups to interchange heroes in
            for i, j in product(group_1, group_2)  # select particular indexes to interchange
        ])
        logger.trace('Swaps shape: {}.', swaps.shape)

        # Let's evolve.
        count_down = CountDown(count(1), self.n_generations_count_down)
        solution = ArenaSolution(enemy=enemy, attackers=[], probability=0.0, probabilities=[])

        for n_generation in count_down:
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
            x = vstack([
                hero_features[self.solutions[:, selector]].sum(axis=1) - defender_features
                for selector, defender_features in zip(team_selectors, defenders_features)
            ])
            ys = numpy.split(self.model.estimator.predict_proba(x)[:, 1], n_actual_teams)

            # Convert individual battle probabilities to the final arena battle probabilities.
            y_reduced = self.reduce_probabilities(*ys)

            # Select top solutions for the next iteration.
            # See also: https://stackoverflow.com/a/23734295/359730
            top_indexes = y_reduced.argpartition(-self.n_keep_solutions)[-self.n_keep_solutions:]

            # All the arrays must be cut to the top indexes, otherwise their rows won't correspond to each other.
            self.solutions = self.solutions[top_indexes, :]
            y_reduced = y_reduced[top_indexes]
            ys = [y[top_indexes] for y in ys]

            # Select the best solution of this generation.
            old_probability = solution.probability
            max_index = y_reduced.argmax()
            solution = ArenaSolution(
                enemy=enemy,
                attackers=[
                    [self.heroes[i] for i in self.solutions[max_index, selector]]
                    for selector in team_selectors
                ],
                probability=y_reduced[max_index],
                probabilities=[y[max_index] for y in ys],
            )
            if solution.probability - old_probability >= 0.00001:
                # The solution has been improved. Give the optimizer another chance to beat it.
                count_down.reset()
                logger.trace('Bump: +{:.3f}%.', 100.0 * (solution.probability - old_probability))
            logger.trace('Generation {:2}: {:.2f}% ({:d})', n_generation, 100.0 * solution.probability, int(count_down))

            # I'm feeling lucky!
            # It makes sense to stop if the probability is already close to 100%.
            if solution.probability > 0.99999:
                break

        return solution

    def make_hero_features(self, hero: Hero) -> ndarray:
        """
        Make hero features 1D-array.
        """
        # noinspection PyUnresolvedReferences
        return numpy.fromiter((hero.features.get(name, 0.0) for name in self.model.feature_names), numpy.float)

    def make_team_features(self, team: List[Hero]) -> ndarray:
        """
        Make team features 2D-array. Shape is number of heroes × number of features.
        """
        return vstack([self.make_hero_features(hero) for hero in team])


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

def swap_permutation(size: int, index_1: int, index_2: int) -> ndarray:
    permutation = arange(size)
    permutation[[index_1, index_2]] = permutation[[index_2, index_1]]
    return permutation


def reduce_normal_arena(y: ndarray) -> ndarray:
    """
    For the normal one-battle arena it's just the probabilities themselves.
    """
    return y


def reduce_grand_arena(y1: ndarray, y2: ndarray, y3: ndarray) -> ndarray:
    """
    Gives probability to win at least two of three battles.
    """
    return y1 * y2 * y3 + y1 * y2 * (1.0 - y3) + y2 * y3 * (1.0 - y1) + y1 * y3 * (1.0 - y2)
