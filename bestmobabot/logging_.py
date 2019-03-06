from __future__ import annotations

import sys
from typing import Iterable

from loguru import logger

import bestmobabot.dataclasses_
from bestmobabot.constants import LOGURU_FORMAT, VERBOSITY_LEVELS
from bestmobabot.telegram import TelegramLogger


def install_logging(verbosity: int):
    logger.stop()
    logger.add(sys.stderr, format=LOGURU_FORMAT, level=VERBOSITY_LEVELS.get(verbosity, 'TRACE'))


def log_rewards(rewards: Iterable[bestmobabot.dataclasses_.Reward], logger_: TelegramLogger = None):
    for reward in rewards:
        reward.log(logger_)
