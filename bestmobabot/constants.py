from typing import Dict, Set

DATABASE_NAME = 'db.sqlite3'
TEAM_SIZE = 5  # heroes
GRAND_TEAMS = 3
GRAND_SIZE = GRAND_TEAMS * TEAM_SIZE  # heroes
MAX_OPEN_ARTIFACT_CHESTS = 5
MAX_ARENA_ENEMIES = 10  # FIXME: make configurable
MAX_GRAND_ARENA_ENEMIES = 10  # FIXME: make configurable
IGNORED_BUFF_IDS = {13, 14, 17, 18, 19}  # These buffs require a hero ID.

# https://heroes.cdnvideo.ru/vk/v0312/lib/lib.json.gz
RECOMMENDED_HEROES: Dict[str, Set[str]] = {
    '1': {'1', '4', '5', '6', '7', '9', '10', '12', '13', '17', '18', '21', '22', '23', '26', '29', '32', '33', '34', '35', '36'},
    '2': {'8', '14', '15', '19', '20', '30', '31'},
    '3': {'2', '3', '11', '16', '25', '24', '27', '28', '37', '38', '39', '40'},
    '4': {'1'},
    '5': {'1'},
    '6': {'1'},
    '7': {'1'},
    '8': {'1'},
    '9': {'1'},
}

# FIXME: obtain from the resources.
COLORS: Dict[int, str] = {
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
