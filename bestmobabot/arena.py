"""
Arena hero selection logic.
"""

import itertools
import math
from operator import attrgetter, itemgetter
from typing import Callable, Iterable, List, Tuple, Optional, TypeVar

import numpy

from bestmobabot import types
from bestmobabot.logger import logger
from bestmobabot.model import feature_names, model
from bestmobabot.responses import ArenaEnemy, Hero

TEAM_SIZE = 5

T1 = TypeVar('T1')
T2 = TypeVar('T2')


def filter_enemies(enemies: Iterable[ArenaEnemy], clan_id: Optional[types.ClanID]) -> List[ArenaEnemy]:
    return [enemy for enemy in enemies if enemy.is_good(clan_id)]


def naive_select_attackers(heroes: Iterable[Hero]) -> Tuple[Hero, ...]:
    """
    Selects the most powerful heroes.
    """
    return tuple(sorted(heroes, key=attrgetter('power'), reverse=True)[:TEAM_SIZE])


def naive_select(enemies: Iterable[ArenaEnemy], heroes: Iterable[Hero]) -> Tuple[ArenaEnemy, Tuple[Hero, ...], float]:
    """
    Select the least powerful enemy and the most powerful heroes.
    """
    enemy = min(enemies, key=attrgetter('power'))
    logger.debug('👊 Naive selector enemy power: %s.', enemy.power)
    return enemy, naive_select_attackers(heroes), -enemy.power


def model_select(enemies: Iterable[ArenaEnemy], heroes: Iterable[Hero]) -> Tuple[ArenaEnemy, Tuple[Hero, ...], float]:
    """
    Select enemy and attackers to maximise win probability.
    """
    # noinspection PyTupleAssignmentBalance
    enemy, attackers, probability = max([
        (enemy, *model_select_attackers(heroes, enemy.heroes))
        for enemy in enemies
    ], key=itemgetter(2))  # type: Tuple[ArenaEnemy, Tuple[Hero, ...], float]
    return enemy, attackers, probability


def model_select_attackers(heroes: Iterable[Hero], defenders: Iterable[Hero]) -> Tuple[Iterable[Hero], float]:
    """
    Select attackers for the given enemy to maximise win probability.
    """
    attackers_list: List[Tuple[Hero, ...]] = list(itertools.combinations(heroes, 5))
    x = numpy.array([get_model_features(attackers) for attackers in attackers_list]) - get_model_features(defenders)
    y: numpy.ndarray = model.predict_proba(x)[:, 1]
    index: int = y.argmax()
    logger.debug('👊 Model selector probability: %.3f.', y[index])
    return attackers_list[index], y[index]


def get_model_features(heroes: Iterable[Hero]) -> numpy.ndarray:
    """
    Build model features for the specified heroes.
    """
    features = {key: value for hero in heroes for key, value in hero.features.items()}
    return numpy.array([features.get(key, 0.0) for key in feature_names])


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
