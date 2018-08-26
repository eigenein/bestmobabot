"""
Logger initialisation.
"""

import logging
from typing import Iterable, TextIO

import coloredlogs

import bestmobabot.responses
from bestmobabot.constants import SPAM


logger = logging.getLogger('bestmobabot')
logging.addLevelName(SPAM, 'SPAM')


def install_logging(verbosity: int, stream: TextIO):
    level = get_logging_level(verbosity)
    coloredlogs.install(
        level,
        fmt='%(asctime)s [%(levelname).1s] %(message)s',
        logger=logger,
        stream=stream,
        field_styles={**coloredlogs.DEFAULT_FIELD_STYLES, 'asctime': {'color': 'green', 'faint': True}},
        datefmt='%b %d %H:%M:%S',
    )


def log_heroes(message: str, heroes: Iterable['bestmobabot.responses.Hero']):
    logger.info(message)
    for hero in sorted(heroes, reverse=True, key=bestmobabot.responses.Hero.order):
        logger.info(f'{hero}')


def log_reward(reward: 'bestmobabot.responses.Reward'):
    reward.log(logger)


def log_rewards(rewards: Iterable['bestmobabot.responses.Reward']):
    for reward in rewards:
        log_reward(reward)


def log_arena_result(result: 'bestmobabot.responses.ArenaResult'):
    logger.info('You won!' if result.win else 'You lose.')
    for i, battle in enumerate(result.battles, start=1):
        logger.info(f'Battle #{i}: {"⭐" * battle.stars if battle.win else "lose."}')
    log_reward(result.reward)


def get_logging_level(verbosity: int) -> int:
    if verbosity == 0:
        return logging.INFO
    if verbosity == 1:
        return logging.DEBUG
    return SPAM
