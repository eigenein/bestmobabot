"""
Loads and extracts useful constants from the game resources.
"""

import gzip
import json
from functools import lru_cache
from typing import Dict, Set

import requests

import bestmobabot.logging_
from bestmobabot import constants


@lru_cache(maxsize=None)
def get_resource(url: str) -> Dict:
    bestmobabot.logging_.logger.info(f'Loading {url}…')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return json.load(gzip.GzipFile(fileobj=response.raw))


def get_translations() -> Dict[str, str]:
    return get_resource(constants.TRANSLATIONS_URL)


def get_library() -> Dict:
    return get_resource(constants.LIBRARY_URL)


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
    missions: Dict[str, Dict] = get_library()['mission']
    return {mission_id for mission_id, mission in missions.items() if mission['isHeroic']}
