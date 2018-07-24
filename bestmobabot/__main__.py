import os
import signal
from datetime import datetime
from typing import TextIO

from click import File, IntRange, command, get_text_stream, option

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logging_ import install_logging, logger
from bestmobabot.resources import get_library, get_translations
from bestmobabot.vk import VK


@command(context_settings={'max_content_width': 120})
@option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='REMIXSID', required=True)
@option('vk_token', '--vk', help='VK.com API token.', envvar='VK_TOKEN', required=True)
@option('-l', '--log-file', help='Log file.', envvar='LOGFILE', type=File('at'), default=get_text_stream('stderr'))
@option('verbosity', '-v', '--verbose', help='Increase verbosity.', count=True)
@option('--no-experience', help='Do not farm experience.', envvar='NO_EXPERIENCE', is_flag=True)
@option('is_trainer', '--trainer', help='Automatically train arena model once a day.', envvar='IS_TRAINER', is_flag=True)
@option('raids', '--raid', help='Raid the mission specified by its ID.', envvar='RAIDS', type=str, multiple=True)
@option('shops', '--shop', help='Buy goods specified by `shopId` and `slotId` every day', envvar='SHOPS', type=(str, str), multiple=True)
@option('friend_ids', '--friend', help='Send daily gift to a friend specified by its ID.', envvar='FRIENDS', type=str, multiple=True)
@option('--arena-skip-clan', 'arena_skip_clans', help='Do not attack members of a clan (title or ID).', envvar='ARENA_SKIP_CLANS', type=str, multiple=True)
@option('--arena-early-stop', help='Minimum win probability to stop (grand) arena enemy search early.', envvar='ARENA_EARLY_STOP', type=float, default=0.95, show_default=True)
@option('--arena-offset', help='Arena schedule offset in seconds.', envvar='ARENA_OFFSET', type=int, default=0, show_default=True)
@option('--arena-teams-limit', help='Greater: better arena attackers but uses more resources.', envvar='ARENA_TEAMS_LIMIT', type=IntRange(min=1), default=20000, show_default=True)
@option('--grand-arena-generations', help='Greater: better grand arena attackers but uses more resources.', envvar='GRAND_ARENA_GENERATIONS', type=IntRange(min=1), default=25, show_default=True)
def main(remixsid: str, vk_token: str, log_file: TextIO, verbosity: int, **kwargs):
    """
    Hero Wars bot.
    """
    signal.signal(signal.SIGTERM, handle_sigterm)
    install_logging(verbosity, log_file)
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
