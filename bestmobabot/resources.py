"""
Loads and extracts useful constants from the game resources.
"""

import gzip
import json
from functools import lru_cache
from typing import Dict

import requests

from bestmobabot.types import *

# FIXME: obtain from the resources.
COLORS = {
    1: 'Белый',
    2: 'Зеленый',
    3: 'Зеленый+1',
    4: 'Синий',
    5: 'Синий+1',
    6: 'Синий+2',
    7: 'Фиолетовый',
    8: 'Фиолетовый+1',
    9: 'Фиолетовый+2',
    10: 'Фиолетовый+3',
    11: 'Оранжевый',
    12: 'Оранжевый+1',
    13: 'Оранжевый+2',
    14: 'Оранжевый+3',
    15: 'Оранжевый+4',
}


@lru_cache(maxsize=None)
def get_resource(url: str) -> Dict:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return json.load(gzip.GzipFile(fileobj=response.raw))


def get_translations() -> Dict[str, str]:
    # FIXME: dynamically find out the latest server version.
    return get_resource('https://heroes.cdnvideo.ru/vk/v0326/locale/ru.json.gz')


def get_library() -> Dict:
    # FIXME: dynamically find out the latest server version.
    # FIXME: unused at the moment (unsure if it gives any benefit).
    return get_resource('https://heroes.cdnvideo.ru/vk/v0334/lib/lib.json.gz')


def hero_name(hero_id: HeroID) -> str:
    return get_translations().get(f'LIB_HERO_NAME_{hero_id}', f'#{hero_id}')


def coin_name(coin_id: str) -> str:
    return get_translations().get(f'LIB_COIN_NAME_{coin_id}', f'#{coin_id}')


def consumable_name(consumable_id: ConsumableID) -> str:
    return get_translations().get(f'LIB_CONSUMABLE_NAME_{consumable_id}', f'#{consumable_id}')


def gear_name(gear_id: str) -> str:
    return get_translations().get(f'LIB_GEAR_NAME_{gear_id}', f'#{gear_id}')


def scroll_name(scroll_id: str) -> str:
    return get_translations().get(f'LIB_SCROLL_NAME_{scroll_id}', f'#{scroll_id}')


def shop_name(shop_id: ShopID) -> str:
    return get_translations().get(f'LIB_SHOP_NAME_{shop_id}', f'#{shop_id}')


def mission_name(mission_id: MissionID) -> str:
    return get_translations().get(f'LIB_MISSION_NAME_{mission_id}', f'#{mission_id}')


def artifact_name(artifact_id: str) -> str:
    return get_translations().get(f'LIB_ARTIFACT_NAME_{artifact_id}', f'#{artifact_id}')
