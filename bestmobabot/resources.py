"""
Loads and extracts useful constants from the game resources.
"""

import gzip
import json
from functools import lru_cache
from typing import Dict, List, Set

import requests
from pydantic import BaseModel

import bestmobabot.logging_
from bestmobabot import constants


class MissionReward(BaseModel):
    gear: Dict[str, int] = {}
    consumable: Dict[str, int] = {}
    fragment_hero: Dict[str, int] = {}

    class Config:
        fields = {'fragment_hero': 'fragmentHero'}


class MissionEnemyDrop(BaseModel):
    reward: MissionReward


class MissionEnemy(BaseModel):
    drops: List[MissionEnemyDrop] = []

    class Config:
        fields = {'drops': 'drop'}


class MissionWave(BaseModel):
    enemies: List[MissionEnemy]


class MissionMode(BaseModel):
    waves: List[MissionWave]


class Mission(BaseModel):
    id: str
    is_heroic: bool
    normal_mode: MissionMode

    class Config:
        fields = {'is_heroic': 'isHeroic', 'normal_mode': 'normalMode'}


class Library(BaseModel):
    missions: Dict[str, Mission]

    class Config:
        fields = {'missions': 'mission'}


@lru_cache(maxsize=None)
def get_resource(url: str) -> str:
    bestmobabot.logging_.logger.info(f'Loading {url}…')
    with requests.get(url) as response:
        response.raise_for_status()
        return gzip.decompress(response.content).decode()


def get_translations() -> Dict[str, str]:
    return json.loads(get_resource(constants.TRANSLATIONS_URL))


@lru_cache(maxsize=None)
def get_library() -> Library:
    return Library.parse_raw(get_resource(constants.LIBRARY_URL))


def hero_name(hero_id: str) -> str:
    return get_translations().get(f'LIB_HERO_NAME_{hero_id}', f'#{hero_id}')


def coin_name(coin_id: str) -> str:
    return get_translations().get(f'LIB_COIN_NAME_{coin_id}', f'#{coin_id}')


def consumable_name(consumable_id: str) -> str:
    return get_translations().get(f'LIB_CONSUMABLE_NAME_{consumable_id}', f'#{consumable_id}')


def gear_name(gear_id: str) -> str:
    return get_translations().get(f'LIB_GEAR_NAME_{gear_id}', f'#{gear_id}')


def scroll_name(scroll_id: str) -> str:
    return get_translations().get(f'LIB_SCROLL_NAME_{scroll_id}', f'#{scroll_id}')


def shop_name(shop_id: str) -> str:
    return get_translations().get(f'LIB_SHOP_NAME_{shop_id}', f'#{shop_id}')


def mission_name(mission_id: str) -> str:
    return get_translations().get(f'LIB_MISSION_NAME_{mission_id}', f'#{mission_id}')


def artifact_name(artifact_id: str) -> str:
    return get_translations().get(f'LIB_ARTIFACT_NAME_{artifact_id}', f'#{artifact_id}')


def titan_artifact_name(artifact_id: str) -> str:
    return get_translations().get(f'LIB_TITAN_ARTIFACT_NAME_{artifact_id}', f'#{artifact_id}')


@lru_cache(maxsize=None)
def get_heroic_mission_ids() -> Set[str]:
    return {
        mission_id
        for mission_id, mission in get_library().missions.items()
        if mission.is_heroic
    }
