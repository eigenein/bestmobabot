from typing import Dict

DATABASE_NAME = 'db.sqlite3'

# Fundamental constants.
TEAM_SIZE = 5  # heroes
GRAND_TEAMS = 3
GRAND_SIZE = GRAND_TEAMS * TEAM_SIZE  # heroes

# Chests control.
MAX_OPEN_ARTIFACT_CHESTS = 5

# Tower control.
TOWER_IGNORED_BUFF_IDS = {13, 14, 17, 18, 19}  # These buffs require a hero ID.

# Arena model training control.
MODEL_SCORING = 'accuracy'
MODEL_N_SPLITS = 5
MODEL_N_ESTIMATORS_CHOICES = [
    5, 10, 15, 20, 25, 30, 35, 40, 45, 50,
    60, 70, 80, 90, 100,
    120, 140, 160, 180, 200,
    250, 300, 350, 400,
]

# Arena iterations control.
ARENA_EARLY_STOP = 0.95
ARENA_MAX_ITERATIONS = 10  # FIXME: make configurable
ARENA_COMBINATIONS_LIMIT = 20000  # FIXME: make configurable
GRAND_ARENA_MAX_ITERATIONS = 10  # FIXME: make configurable
GRAND_ARENA_GENERATIONS = 30  # FIXME: make configurable
GRAND_ARENA_N_KEEP = 200  # FIXME: make configurable
GRAND_ARENA_N_GENERATE = 1000  # FIXME: make configurable

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
