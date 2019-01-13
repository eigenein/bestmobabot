from __future__ import annotations

from typing import Iterable, List

from bestmobabot.dataclasses_ import Hero


def get_hero_ids(team: Iterable[Hero]) -> List[str]:
    return [hero.id for hero in team]


def get_teams_hero_ids(teams: Iterable[Iterable[Hero]]) -> List[List[str]]:
    return [get_hero_ids(team) for team in teams]
