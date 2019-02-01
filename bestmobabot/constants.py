from typing import Dict

# General.
API_TIMEOUT = 10.0
DATABASE_NAME = 'db.sqlite3'
ANALYTICS_URL = 'https://www.google-analytics.com/collect'
ANALYTICS_TID = 'UA-65034198-7'
IP_URL = 'https://ipinfo.io/ip'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'  # noqa

# Resources.
# FIXME: dynamically find out the latest server version. Or at least make configurable.
TRANSLATIONS_URL = 'https://heroes.cdnvideo.ru/vk/v0459/locale/ru.json.gz'
LIBRARY_URL = 'https://heroes.cdnvideo.ru/vk/v0463/lib/lib.json.gz'

# Fundamental constants.
TEAM_SIZE = 5  # heroes
N_GRAND_TEAMS = 3
N_GRAND_HEROES = N_GRAND_TEAMS * TEAM_SIZE  # heroes

# Chests control.
MAX_OPEN_ARTIFACT_CHESTS = 10

# Tower control.
TOWER_IGNORED_BUFF_IDS = {13, 14, 17, 18, 19}  # These buffs require a hero ID.

# Arena model training control.
MODEL_SCORING = 'accuracy'
MODEL_SCORING_ALPHA = 0.95
MODEL_N_SPLITS = 5
MODEL_N_ESTIMATORS_CHOICES = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]
MODEL_PARAM_GRID = {
    'n_estimators': MODEL_N_ESTIMATORS_CHOICES,
    'criterion': ['entropy', 'gini'],
}
MODEL_N_LAST_BATTLES = 20000

# Raids.
RAID_N_HEROIC_TRIES = 3
RAID_N_STARS = 3

# Offers.
OFFER_FARMED_TYPES = ('dailyReward',)

# Shops.
SHOP_IDS = ('1', '4', '5', '6', '8', '9', '10', '11')

# Logging.
LOGURU_FORMAT = ' '.join((
    '<green>{time:MMM DD HH:mm:ss}</green>',
    '<cyan>({name}:{line})</cyan>',
    '<level>[{level:.1}]</level>',
    '<level>{message}</level>',
))
LOGURU_TELEGRAM_FORMAT = '{message}'
VERBOSITY_LEVELS = {
    0: 'INFO',
    1: 'DEBUG',
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

# Experiments.
EXPERIMENT_URL = 'https://www.dropbox.com/s/poahkun7uh5f15u/experiment.py?raw=1'
