import logging
from typing import Union

from bestmobabot.responses import *


logger = logging.getLogger('bestmobabot')


def get_power(enemy: Union[ArenaEnemy, Hero]) -> int:
    return enemy.power
