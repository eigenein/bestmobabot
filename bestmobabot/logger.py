"""
Logger initialisation.
"""

import logging
from typing import Iterable

from bestmobabot import responses


logger = logging.getLogger('bestmobabot')


def log_heroes(message: str, heroes: Iterable[responses.Hero]):
    logger.info('👊 %s %s', message, ' '.join(f'[ {hero} ]' for hero in heroes))


def log_reward(reward: responses.Reward):
    logger.info('📈 %s', reward)


def log_rewards(rewards: Iterable[responses.Reward]):
    for reward in rewards:
        log_reward(reward)


def log_arena_result(result: responses.ArenaResult):
    logger.info('👍 You won!' if result.win else '👎 You lose.')
    for i, battle in enumerate(result.battles, start=1):
        logger.info('👊 Battle #%s: %s.', i, '⭐' * battle.stars if battle.win else 'lose')
    log_reward(result.reward)
