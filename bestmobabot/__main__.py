from datetime import datetime

import IPython
from click import command, option

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.constants import LOGURU_TELEGRAM_FORMAT
from bestmobabot.database import Database
from bestmobabot.logging_ import TelegramHandler, install_logging, logger
from bestmobabot.settings import Settings, SettingsFileParamType
from bestmobabot.tracking import get_version
from bestmobabot.vk import VK


@command(context_settings={'max_content_width': 120})
@option(
    '--settings',
    help='Settings file.',
    default='settings.yaml',
    show_default=True,
    envvar='BESTMOBABOT_SETTINGS',
    show_envvar=True,
    type=SettingsFileParamType(Settings),
)
@option(
    'verbosity', '-v', '--verbose',
    help='Increase verbosity.',
    envvar='BESTMOBABOT_VERBOSITY',
    show_envvar=True,
    count=True,
)
@option('--shell', is_flag=True, help='Start interactive shell after initialization instead of normal run.')
def main(settings: Settings, verbosity: int, shell: bool):
    """
    Hero Wars game bot 🏆
    """
    install_logging(verbosity)
    logger.info(f'Bot is starting. Version: {get_version()}.')

    with Database(constants.DATABASE_NAME) as db, API(db, settings) as api, Bot(db, api, VK(settings), settings) as bot:
        api.start()
        bot.start()
        if settings.telegram and settings.telegram.token and settings.telegram.chat_id:
            logger.info('Adding Telegram logging handler.')
            logger.add(TelegramHandler(settings.telegram, bot.user.name), level='INFO', format=LOGURU_TELEGRAM_FORMAT)
        logger.info(f'Welcome «{bot.user.name}»! Your game time is {datetime.now(bot.user.tz):%H:%M:%S %Z}.')
        logger.info('Next day starts at {:%H:%M:%S %Z}.', bot.user.next_day.astimezone(bot.user.tz))
        if not shell:
            bot.run()
        else:
            IPython.embed()


if __name__ == '__main__':
    main(auto_envvar_prefix='BESTMOBABOT')
