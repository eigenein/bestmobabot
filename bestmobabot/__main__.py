import signal
from datetime import datetime, timedelta
from typing import TextIO, Tuple

import click
import coloredlogs

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logger import logger
from bestmobabot.resources import get_translations
from bestmobabot.vk import VK


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='BESTMOBABOT_REMIXSID', required=True)
@click.option('vk_token', '--vk', help='VK.com API token.', envvar='BESTMOBABOT_VK_TOKEN', required=True)
@click.option('--no-experience', help='Do not farm experience.', envvar='BESTMOBABOT_NO_EXPERIENCE', is_flag=True)
@click.option('is_trainer', '--trainer', help='Automatically train arena model.', envvar='BESTMOBABOT_TRAINER', is_flag=True)
@click.option('raids', '--raid', help='Raid the mission specified by its ID and number of raids per day.', envvar='BESTMOBABOT_RAID', type=(str, int), multiple=True)
@click.option('shops', '--shop', help='Buy goods specified by shop_id and slot_id every day', envvar='BESTMOBABOT_SHOP', type=(str, str), multiple=True)
@click.option('arena_offset', '--arena-offset', help='Arena schedule offset in seconds.', envvar='BESTMOBABOT_ARENA_OFFSET', type=int, default=0)
@click.option('-v', '--verbose', help='Increase verbosity.', is_flag=True)
@click.option('-l', '--log-file', help='Log file.', envvar='BESTMOBABOT_LOGFILE', type=click.File('at'), default=click.get_text_stream('stderr'))
def main(
    remixsid: str,
    vk_token: str,
    no_experience: bool,
    is_trainer: bool,
    raids: Tuple[Tuple[str, int], ...],
    shops: Tuple[Tuple[str, str], ...],
    arena_offset: int,
    verbose: bool,
    log_file: TextIO,
):
    """
    Hero Wars bot.
    """
    signal.signal(signal.SIGTERM, handle_sigterm)
    level = 'DEBUG' if verbose else 'INFO'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=level, logger=logger, stream=log_file)
    logger.info('🤖 Bot is starting.')

    get_translations()  # prefetch game translations

    with Database(constants.DATABASE_NAME) as db, API(db, remixsid) as api:
        with Bot(db, api, VK(vk_token), no_experience, is_trainer, list(raids), list(shops), timedelta(seconds=arena_offset)) as bot:
            api.start()
            bot.start()
            logger.info(f'👋 Welcome {bot.user.name}! Your game time is {datetime.now(bot.user.tz):%H:%M:%S}.')
            logger.info('👋 Next day starts at %s.', bot.user.next_day)
            bot.run()


# noinspection PyUnusedLocal
def handle_sigterm(signum, frame):
    raise KeyboardInterrupt


if __name__ == '__main__':
    main()
