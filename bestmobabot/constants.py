from typing import Dict

API_TIMEOUT = 10.0
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
MODEL_SCORING_ALPHA = 0.95
MODEL_N_SPLITS = 5
MODEL_N_ESTIMATORS_CHOICES = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100, 150, 200]

# Raids.
RAID_N_HEROIC_TRIES = 3
RAID_N_STARS = 3

# Offers.
OFFER_FARMED_TYPES = ('dailyReward',)

# Logging.
SPAM = 5

# Arena iterations control.
# FIXME: make configurable.
ARENA_MAX_PAGES = 15
GRAND_ARENA_MAX_PAGES = 15
GRAND_ARENA_N_KEEP = 200
GRAND_ARENA_N_GENERATE = 1000

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
