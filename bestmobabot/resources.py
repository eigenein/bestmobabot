"""
Loads and extracts useful constants from the game resources.
"""

import gzip
import json
from functools import lru_cache
from typing import Dict

import requests

from bestmobabot.types import *

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


def hero_name(hero_id: HeroID) -> str:
    return get_translations().get(f'LIB_HERO_NAME_{hero_id}', f'Hero #{hero_id}')
