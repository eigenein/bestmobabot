"""
Logger initialisation.
"""

import logging
from typing import Iterable

import bestmobabot.responses


logger = logging.getLogger('bestmobabot')


def log_heroes(emoji: str, message: str, heroes: Iterable['bestmobabot.responses.Hero']):
    logger.info(f'{emoji} {message}')
    for hero in sorted(heroes, reverse=True, key=bestmobabot.responses.Hero.order):
        logger.info(f'{emoji} {hero}')


def log_reward(reward: 'bestmobabot.responses.Reward'):
    reward.log(logger)


def log_rewards(rewards: Iterable['bestmobabot.responses.Reward']):
    for reward in rewards:
        log_reward(reward)


def log_arena_result(result: 'bestmobabot.responses.ArenaResult'):
    logger.info('👍 You won!' if result.win else '👎 You lose.')
    for i, battle in enumerate(result.battles, start=1):
        logger.info(f'👊 Battle #{i}: {"⭐" * battle.stars if battle.win else "lose."}')
    log_reward(result.reward)
