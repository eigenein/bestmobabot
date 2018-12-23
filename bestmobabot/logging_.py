"""
Logger initialisation.
"""

from __future__ import annotations

import sys
from typing import Iterable

from loguru import logger

import bestmobabot.responses
from bestmobabot.constants import LOGURU_FORMAT, VERBOSITY_LEVELS


def install_logging(verbosity: int):
    logger.stop()
    logger.add(sys.stderr, format=LOGURU_FORMAT, level=VERBOSITY_LEVELS.get(verbosity, 'TRACE'))


def log_heroes(message: str, heroes: Iterable[bestmobabot.responses.Hero]):
    logger.info(message)
    for hero in sorted(heroes, reverse=True, key=bestmobabot.responses.Hero.order):
        logger.info(f'{hero}')


def log_rewards(rewards: Iterable[bestmobabot.responses.Reward]):
    for reward in rewards:
        reward.log()
