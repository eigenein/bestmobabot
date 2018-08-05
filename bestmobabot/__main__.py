from datetime import datetime
from typing import TextIO

from click import File, command, get_text_stream, option

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logging_ import install_logging, logger
from bestmobabot.resources import get_library, get_translations
from bestmobabot.settings import Settings, SettingsFileParamType
from bestmobabot.tracking import get_version
from bestmobabot.vk import VK


@command()
@option(
    '--settings',
    help='Settings file.',
    envvar='SETTINGS',
    type=SettingsFileParamType(Settings),
    required=True,
)
@option('-l', '--log-file', help=f'Log file.', envvar='LOGFILE', type=File('at'), default=get_text_stream('stderr'))
@option('verbosity', '-v', '--verbose', help='Increase verbosity.', envvar='VERBOSITY', count=True)
def main(settings: Settings, log_file: TextIO, verbosity: int):
    """
    Hero Wars bot.
    """
    install_logging(verbosity, log_file)
    logger.info(f'🤖 Bot is starting. Version: {get_version()}.')

    # Prefetch game resources.
    get_library()
    get_translations()

    with Database(constants.DATABASE_NAME) as db, API(db, settings) as api, Bot(db, api, VK(settings), settings) as bot:
        api.start()
        bot.start()
        logger.info(f'👋 Welcome {bot.user.name}! Your game time is {datetime.now(bot.user.tz):%H:%M:%S}.')
        logger.info('👋 Next day starts at %s.', bot.user.next_day)
        bot.run()


if __name__ == '__main__':
    main()
