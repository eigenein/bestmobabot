import signal
from datetime import datetime
from typing import TextIO, Tuple

import click
import coloredlogs

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logger import logger
from bestmobabot.resources import get_translations


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='BESTMOBABOT_REMIXSID', required=True)
@click.option('--no-experience', help='Do not farm experience.', envvar='BESTMOBABOT_NO_EXPERIENCE', is_flag=True)
@click.option('raids', '--raid', help='Raid the mission specified by its ID and number of raids per day.', envvar='BESTMOBABOT_RAID', type=(str, int), multiple=True)
@click.option('-v', '--verbose', help='Increase verbosity.', is_flag=True)
@click.option('-l', '--log-file', help='Log file.', envvar='BESTMOBABOT_LOGFILE', type=click.File('at'), default=click.get_text_stream('stderr'))
@click.option('shops', '--shop', help='Buy goods specified by shop_id and slot_id every day', envvar='BESTMOBABOT_SHOP', type=(str, str), multiple=True)
def main(
    remixsid: str,
    no_experience: bool,
    raids: Tuple[Tuple[str, int], ...],
    verbose: bool,
    log_file: TextIO,
    shops: Tuple[Tuple[str, str], ...],
):
    """
    Hero Wars bot.
    """
    signal.signal(signal.SIGTERM, handle_sigterm)
    level = 'DEBUG' if verbose else 'INFO'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=level, logger=logger, stream=log_file)
    logger.info('🤖 Bot is starting.')

    get_translations()  # prefetch game translations

    with Database(constants.DATABASE_NAME) as db, API(db, remixsid) as api, Bot(db, api, no_experience, list(raids), list(shops)) as bot:
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
