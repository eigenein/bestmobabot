from datetime import datetime

import IPython
from click import command, option
from requests import Session
from requests.adapters import HTTPAdapter

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

    with Session() as session, Database(constants.DATABASE_NAME) as db:
        session.mount('https://', HTTPAdapter(max_retries=5))

        api = API(session, db, settings)
        bot = Bot(db, api, VK(session, settings), settings)

        api.prepare()
        bot.prepare()

        if settings.telegram and settings.telegram.token and settings.telegram.chat_id:
            # Deprecated in favor of explicit notifications.
            logger.info('Adding Telegram logging handler.')
            logger.add(
                TelegramHandler(settings.telegram, bot.user.name),
                level='INFO',
                format=LOGURU_TELEGRAM_FORMAT,
            )

        logger.info('Welcome «{}»!', bot.user.name)
        logger.info('Game time: {:%H:%M:%S %Z}', datetime.now(bot.user.tz))
        logger.info('Next day starts at {:%H:%M:%S %Z}.', bot.user.next_day.astimezone(bot.user.tz))

        if not shell:
            bot.run()
        else:
            IPython.embed()


if __name__ == '__main__':
    main(auto_envvar_prefix='BESTMOBABOT')
