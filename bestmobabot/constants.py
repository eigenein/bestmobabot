from typing import Dict

DATABASE_NAME = 'db.sqlite3'

# Fundamental constants.
TEAM_SIZE = 5  # heroes
GRAND_TEAMS = 3
GRAND_SIZE = GRAND_TEAMS * TEAM_SIZE  # heroes

# Chests control.
MAX_OPEN_ARTIFACT_CHESTS = 5

# Tower control.
IGNORED_BUFF_IDS = {13, 14, 17, 18, 19}  # These buffs require a hero ID.

# Arena model training control.
SCORING = 'accuracy'
N_ITERATIONS = 25
N_SPLITS = 5
MAX_N_ESTIMATORS = 250

# Arena iterations control.
ARENA_EARLY_STOP = 0.99
MAX_ARENA_ITERATIONS = 10  # FIXME: make configurable
MAX_GRAND_ARENA_ITERATIONS = 10  # FIXME: make configurable

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
