"""
Arena hero selection logic.
"""

import math
from functools import reduce
from itertools import combinations
from operator import attrgetter, itemgetter
from typing import Callable, Iterable, List, Tuple, Optional, TypeVar

import numpy

from bestmobabot import types
from bestmobabot.logger import logger
from bestmobabot.model import model
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

def model_select_attackers(heroes: Iterable[Hero], defenders: Iterable[Hero], verbose: bool = True) -> Tuple[List[Hero], float]:
    """
    Select attackers for the given enemy to maximise win probability.
    """
    attackers_list = [list(attackers) for attackers in combinations(heroes, TEAM_SIZE)]
    x = numpy.array([get_model_features(attackers) for attackers in attackers_list]) - get_model_features(defenders)
    y: numpy.ndarray = model.predict_proba(x)[:, 1]
    index: int = y.argmax()
    if verbose:
        logger.debug('👊 Test probability: %.1f%%.', 100.0 * y[index])
    return attackers_list[index], y[index]


def model_grand_select_attackers_slow(heroes: Iterable[Hero], defender_teams: Iterable[Iterable[Hero]]) -> Tuple[Tuple[List[Hero], ...], float]:
    """
    Select 3 teams of attackers for the given enemy to maximise win probability.
    It's very memory-consuming and slow.
    """

    # Select GRAND_SIZE most powerful heroes. Otherwise, we would had to check a lot more combinations.
    heroes = tuple(sorted(heroes, key=attrgetter('power'), reverse=True)[:GRAND_SIZE])

    # Construct possible options to choose teams.
    # FIXME: ~5 sec.
    logger.debug('👊 Generating teams…')
    teams_choices = tuple(choose_multiple(heroes, GRAND_TEAMS, TEAM_SIZE))

    # Construct GRAND_TEAMS arrays for prediction. Each array consists of possibilities for only one team.
    # FIXME: ~15 sec.
    logger.debug('👊 Constructing attackers features…')
    xs = [
        numpy.array([get_model_features(attackers) for attackers in team_attackers])
        for team_attackers in zip(*teams_choices)
    ]

    # Subtract defenders features as in model_select_attackers.
    logger.debug('👊 Applying defenders features…')
    for x, defenders in zip(xs, defender_teams):
        x -= get_model_features(defenders)

    # Predict probabilities in each X. Got 3 Y-vectors with probabilities for each team.
    p1, p2, p3 = (model.predict_proba(x)[:, 1] for x in xs)

    # Compute probability of 2 or 3 successes out of 3 trials.
    # https://en.wikipedia.org/wiki/Poisson_binomial_distribution
    y = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)

    # Ok, now choose the teams with the highest win probability as usual.
    index: int = y.argmax()
    logger.debug('👊 Test probability: %.1f%% (from %.1f%%, %.1f%% and %.1f%%).', 100.0 * y[index], 100.0 * p1[index], 100.0 * p2[index], 100.0 * p3[index])
    return teams_choices[index], y[index]


def model_grand_select_attackers_light(heroes: Iterable[Hero], defender_teams: Iterable[Iterable[Hero]]) -> Tuple[Tuple[List[Hero], ...], float]:
    """
    Select 3 teams of attackers for the given enemy to maximise win probability.
    It's not giving the best solution.
    """

    heroes = tuple(heroes)
    defender_teams = tuple(defender_teams)

    # First try to estimate which enemy team is the strongest for us. We're not going to beat it.
    win_probabilities = [model_select_attackers(heroes, defenders, verbose=False)[1] for defenders in defender_teams]
    p1, p2, p3 = win_probabilities
    logger.debug('👊 Estimated probabilities: %.1f%% | %.1f%% | %.1f%%.', 100.0 * p1, 100.0 * p2, 100.0 * p3)
    order = sorted(range(GRAND_TEAMS), key=win_probabilities.__getitem__)

    # So, we ignore the strongest enemy.
    # And from the other ones we first try to beat the strongest one.
    # The ignored one is checked the last.
    probabilities: List[float] = [0.0] * GRAND_TEAMS
    attackers_teams: List[List[Hero]] = [[]] * GRAND_TEAMS
    for i in (*order[1:], order[0]):
        attackers, probability = model_select_attackers(heroes, defender_teams[i], verbose=False)
        attackers_teams[i] = attackers
        probabilities[i] = probability
        # Exclude used heroes.
        used_heroes = {hero.id for hero in attackers}
        heroes = tuple(hero for hero in heroes if hero.id not in used_heroes)

    # Compute probability of 2 or 3 successes out of 3 trials.
    # https://en.wikipedia.org/wiki/Poisson_binomial_distribution
    p1, p2, p3 = probabilities
    p = p1 * p2 * p3 + p1 * p2 * (1.0 - p3) + p2 * p3 * (1.0 - p1) + p1 * p3 * (1.0 - p2)
    logger.debug('👊 Test probability: %.1f%% (%.1f%% | %.1f%% | %.1f%%).', 100.0 * p, 100.0 * p1, 100.0 * p2, 100.0 * p3)
    return tuple(attackers_teams), p


# Features construction.
# ----------------------------------------------------------------------------------------------------------------------

def get_model_features(heroes: Iterable[Hero]) -> numpy.ndarray:
    """
    Build model features for the specified heroes.
    """
    return reduce(numpy.add, (hero.features for hero in heroes))


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


def choose_multiple(items: Iterable[T], n: int, k: int) -> Iterable[Tuple[List[T], ...]]:
    """
    Choose n groups of size k.
    """
    if n == 0:
        yield ()
        return
    for head in choose_multiple(items, n - 1, k):
        used_keys = {item.id for sub_items in head for item in sub_items}
        for tail in combinations((item for item in items if item.id not in used_keys), k):
            yield (*head, [*tail])
