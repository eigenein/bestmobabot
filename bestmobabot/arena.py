"""
Arena hero selection logic.
"""

import math
from itertools import combinations
from operator import attrgetter, itemgetter
from typing import Any, Callable, Iterable, List, Tuple, Optional, TypeVar

import numpy

from bestmobabot import types
from bestmobabot.logger import logger
from bestmobabot.model import feature_names, model
from bestmobabot.responses import ArenaEnemy, GrandArenaEnemy, Hero

TEAM_SIZE = 5  # heroes
GRAND_TEAMS = 3
GRAND_SIZE = GRAND_TEAMS * TEAM_SIZE  # heroes

TArenaEnemy = TypeVar('TArenaEnemy', ArenaEnemy, GrandArenaEnemy)
TArenaHeroes = TypeVar('TArenaHeroes')
T = TypeVar('T')
T1 = TypeVar('T1')
T2 = TypeVar('T2')


# Shared for both arenas.
# ----------------------------------------------------------------------------------------------------------------------

def filter_enemies(enemies: Iterable[TArenaEnemy], clan_id: Optional[types.ClanID]) -> List[TArenaEnemy]:
    return [enemy for enemy in enemies if enemy.user is not None and not enemy.user.is_from_clan(clan_id)]


def naive_select_attackers(heroes: Iterable[Hero]) -> List[Hero]:
    """
    Selects the most powerful heroes.
    """
    return sorted(heroes, key=attrgetter('power'), reverse=True)[:TEAM_SIZE]


def select_enemy(
    enemies: Iterable[TArenaEnemy],
    heroes: Iterable[Hero],
    select_attackers: Callable[[Iterable[Hero], TArenaHeroes], Tuple[TArenaHeroes, float]],
) -> Tuple[TArenaEnemy, TArenaHeroes, float]:
    """
    Select enemy and attackers to maximise win probability.
    """
    # noinspection PyTupleAssignmentBalance
    enemy, attackers, probability = max([
        (enemy, *select_attackers(heroes, enemy.heroes))
        for enemy in enemies
    ], key=itemgetter(2))  # type: Tuple[TArenaEnemy, TArenaHeroes, float]
    return enemy, attackers, probability


# Attackers selection.
# ----------------------------------------------------------------------------------------------------------------------

def model_select_attackers(heroes: Iterable[Hero], defenders: Iterable[Hero]) -> Tuple[List[Hero], float]:
    """
    Select attackers for the given enemy to maximise win probability.
    """
    attackers_list = [list(attackers) for attackers in combinations(heroes, TEAM_SIZE)]
    x = numpy.array([get_model_features(attackers) for attackers in attackers_list]) - get_model_features(defenders)
    y: numpy.ndarray = model.predict_proba(x)[:, 1]
    index: int = y.argmax()
    logger.debug('👊 Test probability: %.1f%%.', 100.0 * y[index])
    return attackers_list[index], y[index]


def model_grand_select_attackers(heroes: Iterable[Hero], defender_teams: Iterable[Iterable[Hero]]) -> Tuple[Tuple[List[Hero], ...], float]:
    """
    Select 3 teams of attackers for the given enemy to maximise win probability.
    """

    # Select GRAND_SIZE most powerful heroes. Otherwise, we would had to check a lot more combinations.
    heroes = sorted(heroes, key=attrgetter('power'), reverse=True)[:GRAND_SIZE]

    # Construct possible options to choose teams.
    teams_choices = list(choose_multiple(heroes, GRAND_TEAMS, TEAM_SIZE, attrgetter('id')))

    # Construct GRAND_TEAMS arrays for prediction. Each array consists of possibilities for only one team.
    xs = [
        numpy.array([get_model_features(attackers) for attackers in team_attackers])
        for team_attackers in zip(*teams_choices)
    ]

    # Subtract defenders features as in model_select_attackers.
    for x, defenders in zip(xs, defender_teams):
        x -= get_model_features(defenders)

    # Predict probabilities in each X. Got 3 Y-vectors with probabilities for each team.
    p1, p2, p3 = (model.predict_proba(x)[:, 1] for x in xs)

    # Compute probability of 2 or 3 successes out of 3 trials.
    # https://en.wikipedia.org/wiki/Poisson_binomial_distribution
    y = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)

    # Ok, now choose the teams with the highest win probability as usual.
    index: int = y.argmax()
    logger.debug('👊 Test probability: %.1f%%.', 100.0 * y[index])
    return teams_choices[index], y[index]


# Features construction.
# ----------------------------------------------------------------------------------------------------------------------

def get_model_features(heroes: Iterable[Hero]) -> numpy.ndarray:
    """
    Build model features for the specified heroes.
    """
    features = {key: value for hero in heroes for key, value in hero.features.items()}
    return numpy.array([features.get(key, 0.0) for key in feature_names])


# Utilities.
# ----------------------------------------------------------------------------------------------------------------------

def secretary_max(items: Iterable[T1], n: int, key: Optional[Callable[[T1], T2]] = None) -> Tuple[T1, T2]:
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
        if max_key is None or item_key > max_key:
            break
    # noinspection PyUnboundLocalVariable
    return item, item_key


def choose_multiple(items: Iterable[T], n: int, k: int, key: Callable[[T], Any]) -> Iterable[Tuple[List[T], ...]]:
    """
    Choose n groups of size k.
    """
    if n == 0:
        yield ()
        return
    for head in choose_multiple(items, n - 1, k, key):
        used_keys = {key(item) for sub_items in head for item in sub_items}
        for tail in combinations((item for item in items if key(item) not in used_keys), k):
            yield (*head, list(tail))
