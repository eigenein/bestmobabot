"""
Arena hero selection logic.
"""

import itertools
import math
from operator import attrgetter, itemgetter
from typing import Any, Callable, Iterable, List, Tuple, TypeVar

import numpy

from bestmobabot.logger import logger
from bestmobabot.model import feature_names, model
from bestmobabot.responses import ArenaEnemy, Hero

TEAM_SIZE = 5

T = TypeVar('T')


def naive_select_attackers(heroes: Iterable[Hero]) -> Tuple[Hero, ...]:
    """
    Selects the most powerful heroes.
    """
    return tuple(sorted(heroes, key=attrgetter('power'), reverse=True)[:TEAM_SIZE])


def naive_select(enemies: Iterable[ArenaEnemy], heroes: Iterable[Hero]) -> Tuple[ArenaEnemy, Tuple[Hero, ...]]:
    """
    Select the least powerful enemy and the most powerful heroes.
    """
    return min(enemies, key=attrgetter('power')), naive_select_attackers(heroes)


def model_select(enemies: Iterable[ArenaEnemy], heroes: Iterable[Hero]) -> Tuple[ArenaEnemy, Tuple[Hero, ...]]:
    """
    Select enemy and attackers to maximise win probability.
    """
    # noinspection PyTupleAssignmentBalance
    probability, attackers, enemy = max([
        (*model_select_attackers(heroes, enemy.heroes), enemy)
        for enemy in enemies
    ], key=itemgetter(0))  # type: Tuple[float, Tuple[Hero, ...], ArenaEnemy]

    # Print debugging info.
    logger.info('👊 Attackers:')
    for attacker in attackers:
        logger.info('👊 %s', attacker)
    logger.info('👊 Defenders:')
    for defender in enemy.heroes:
        logger.info('👊 %s', defender)
    logger.info('👊 Chance: %.1f%%', probability * 100.0)

    return enemy, attackers


def model_select_attackers(heroes: Iterable[Hero], defenders: Iterable[Hero]) -> (float, Iterable[Hero]):
    """
    Select attackers for the given enemy to maximise win probability.
    """
    attackers_list: List[Tuple[Hero, ...]] = list(itertools.combinations(heroes, 5))
    x = numpy.array([get_model_features(attackers) for attackers in attackers_list]) - get_model_features(defenders)
    y: numpy.ndarray = model.predict_proba(x)[:, 1]
    index: int = y.argmax()
    return y[index], attackers_list[index]


def get_model_features(heroes: Iterable[Hero]) -> numpy.ndarray:
    """
    Build model features for the specified heroes.
    """
    features = {key: value for hero in heroes for key, value in hero.features.items()}
    return numpy.array([features.get(key, 0.0) for key in feature_names])


def select_best(items: Iterable[T], n: int, key: Callable[[T], Any]) -> T:
    """
    https://en.wikipedia.org/wiki/Secretary_problem
    """
    items: Iterable[T] = itertools.islice(items, round(n / math.e), None)
    # TODO
