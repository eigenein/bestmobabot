import os
import signal
from datetime import datetime
from typing import TextIO

import click

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logger import install_logging, logger
from bestmobabot.resources import get_library, get_translations
from bestmobabot.vk import VK


@click.command(context_settings={'max_content_width': 120})
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='REMIXSID', required=True)
@click.option('vk_token', '--vk', help='VK.com API token.', envvar='VK_TOKEN', required=True)
@click.option('-l', '--log-file', help='Log file.', envvar='LOGFILE', type=click.File('at'), default=click.get_text_stream('stderr'))
@click.option('verbosity', '-v', '--verbose', help='Increase verbosity.', count=True)
@click.option('--no-experience', help='Do not farm experience.', envvar='NO_EXPERIENCE', is_flag=True)
@click.option('is_trainer', '--trainer', help='Automatically train arena model once a day.', envvar='IS_TRAINER', is_flag=True)
@click.option('raids', '--raid', help='Raid the mission specified by its ID.', envvar='RAIDS', type=str, multiple=True)
@click.option('shops', '--shop', help='Buy goods specified by shop_id and slot_id every day', envvar='SHOPS', type=(str, str), multiple=True)
@click.option('friend_ids', '--friend', help='Send daily gift to a friend specified by its ID.', envvar='FRIENDS', type=str, multiple=True)
@click.option('--arena-early-stop', help='Minimum win probability to stop (grand) arena enemy search early.', envvar='ARENA_EARLY_STOP', type=float, default=0.95, show_default=True)
@click.option('--arena-offset', help='Arena schedule offset in seconds.', envvar='ARENA_OFFSET', type=int, default=0, show_default=True)
@click.option('--arena-teams-limit', help='Greater: better arena attackers but uses more resources.', envvar='ARENA_TEAMS_LIMIT', type=int, default=20000, show_default=True)
@click.option('--grand-arena-generations', help='Greater: better grand arena attackers but uses more resources.', envvar='GRAND_ARENA_GENERATIONS', type=int, default=35, show_default=True)
def main(remixsid: str, vk_token: str, log_file: TextIO, verbosity: int, **kwargs):
    """
    Hero Wars bot.
    """
    signal.signal(signal.SIGTERM, handle_sigterm)
    install_logging(logger, verbosity, log_file)
    logger.info('🤖 Bot is starting.')

    # Prefetch game resources.
    get_library()
    get_translations()

    with Database(constants.DATABASE_NAME) as db, API(db, remixsid) as api:
        with Bot(db, api, VK(vk_token), **kwargs) as bot:
            api.start()
            bot.start()
            logger.info(f'👋 Welcome {bot.user.name}! Your game time is {datetime.now(bot.user.tz):%H:%M:%S}.')
            logger.info('👋 Next day starts at %s.', bot.user.next_day)
            bot.run()


# noinspection PyUnusedLocal
def handle_sigterm(signum, frame):
    logger.info(f'👋 SIGTERM received. Bye-bye!{os.linesep}')
    raise KeyboardInterrupt


if __name__ == '__main__':
    main()
