from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Generic, Iterable, List, Optional, Sequence, TypeVar

from bestmobabot import constants
from bestmobabot.dataclasses_ import Hero

T = TypeVar('T')


@dataclass
class KnapsackSolution(Generic[T]):
    items: List[T]
    value: int


def get_hero_ids(team: Iterable[Hero]) -> List[str]:
    return [hero.id for hero in team]


def get_teams_hero_ids(teams: Iterable[Iterable[Hero]]) -> List[List[str]]:
    return [get_hero_ids(team) for team in teams]


def get_team_power(team: Iterable[Hero]) -> int:
    return sum(hero.power for hero in team)


def find_expedition_team(heroes: Iterable[Hero], min_power: int) -> Optional[Sequence[Hero]]:
    best_power = None
    best_team = None

    for team in combinations(heroes, constants.TEAM_SIZE):
        power = get_team_power(team)
        if power < min_power:
            continue
        if best_power is None or best_power > power:
            best_power = power
            best_team = team

    return best_team
