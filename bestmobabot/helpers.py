from __future__ import annotations

from itertools import combinations
from operator import attrgetter
from typing import Iterable, List, Optional, Sequence, TypeVar

from bestmobabot import constants
from bestmobabot.dataclasses_ import Hero, Unit

TUnit = TypeVar('TUnit', bound=Unit)


def get_unit_ids(team: Iterable[TUnit]) -> List[str]:
    return [hero.id for hero in team]


def get_teams_unit_ids(teams: Iterable[Iterable[TUnit]]) -> List[List[str]]:
    return [get_unit_ids(team) for team in teams]


def get_team_power(team: Iterable[TUnit]) -> int:
    return sum(hero.power for hero in team)


def naive_select_attackers(units: Iterable[TUnit], count: int = constants.TEAM_SIZE) -> List[TUnit]:
    """
    Selects the most powerful units.
    """
    return sorted(units, key=attrgetter('power'), reverse=True)[:count]


def find_expedition_team(heroes: Iterable[Hero], min_power: int) -> Optional[Sequence[Hero]]:
    best_power: Optional[int] = None
    best_team = None

    for team in combinations(heroes, constants.TEAM_SIZE):
        power = get_team_power(team)
        if power < min_power:
            continue
        if best_power is None or best_power > power:
            best_power = power
            best_team = team

    return best_team
