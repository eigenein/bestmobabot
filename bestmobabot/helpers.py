from __future__ import annotations

from itertools import combinations
from operator import attrgetter
from typing import Iterable, List, Optional, Sequence

from bestmobabot import constants
from bestmobabot.dataclasses_ import Hero


def get_hero_ids(team: Iterable[Hero]) -> List[str]:
    return [hero.id for hero in team]


def get_teams_hero_ids(teams: Iterable[Iterable[Hero]]) -> List[List[str]]:
    return [get_hero_ids(team) for team in teams]


def get_team_power(team: Iterable[Hero]) -> int:
    return sum(hero.power for hero in team)


def naive_select_attackers(heroes: Iterable[Hero], count: int = constants.TEAM_SIZE) -> List[Hero]:
    """
    Selects the most powerful heroes.
    """
    return sorted(heroes, key=attrgetter('power'), reverse=True)[:count]


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
