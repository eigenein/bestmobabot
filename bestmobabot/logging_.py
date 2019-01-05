"""
Logger initialisation.
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import suppress
from time import time
from typing import Iterable

import requests
from loguru import logger

import bestmobabot.dataclasses_
from bestmobabot.constants import LOGURU_FORMAT, VERBOSITY_LEVELS
from bestmobabot.settings import TelegramSettings

session = requests.Session()


class TelegramHandler(logging.Handler):
    def __init__(self, settings: TelegramSettings, user_name: str):
        super().__init__()
        self.token = settings.token
        self.chat_id = settings.chat_id
        self.user_name = user_name
        self.last_emit_time = 0
        self.messages = []

    def emit(self, record: logging.LogRecord):
        message = record.getMessage()
        self.messages.append(message)
        if not message.endswith(os.linesep) and time() - self.last_emit_time < 5:
            # Quick and dirty rate limiter.
            # Emit messages if 5 seconds have elapsed or if the last message ends with '\n'.
            return
        with suppress(Exception):
            session.post(f'https://api.telegram.org/bot{self.token}/sendMessage', json={
                'chat_id': self.chat_id,
                'text': f'*{self.user_name}*:\n\n`{os.linesep.join(self.messages).rstrip()}`',
                'parse_mode': 'Markdown',
                'disable_notification': True,
            })
        self.last_emit_time = time()
        self.messages.clear()


def install_logging(verbosity: int):
    logger.stop()
    logger.add(sys.stderr, format=LOGURU_FORMAT, level=VERBOSITY_LEVELS.get(verbosity, 'TRACE'))


def log_heroes(message: str, heroes: Iterable[bestmobabot.dataclasses_.Hero]):
    logger.info(message)
    for hero in sorted(heroes, reverse=True):
        logger.info(f'{hero}')


def log_rewards(rewards: Iterable[bestmobabot.dataclasses_.Reward]):
    for reward in rewards:
        reward.log()
