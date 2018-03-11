"""
Logger initialisation.
"""

import logging
from typing import Iterable

from bestmobabot.responses import *


logger = logging.getLogger('bestmobabot')


def log_heroes(message: str, heroes: Iterable[Hero]):
    logger.info('👊 %s %s', message, ' '.join(f'◀ {hero} ▶' for hero in sorted(heroes, reverse=True, key=Hero.order)))


def log_reward(reward: Reward):
    logger.info('📈 %s', reward)


def log_rewards(rewards: Iterable[Reward]):
    for reward in rewards:
        log_reward(reward)


def log_arena_result(result: ArenaResult):
    logger.info('👍 You won!' if result.win else '👎 You lose.')
    for i, battle in enumerate(result.battles, start=1):
        logger.info('👊 Battle #%s: %s.', i, '⭐' * battle.stars if battle.win else 'lose')
    log_reward(result.reward)
