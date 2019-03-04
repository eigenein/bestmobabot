from datetime import datetime

import IPython
from click import command, option
from requests import Session
from requests.adapters import HTTPAdapter

from bestmobabot import constants
from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.database import Database
from bestmobabot.logging_ import install_logging, logger
from bestmobabot.settings import Settings, SettingsFileParamType
from bestmobabot.telegram import Telegram
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

        telegram = Telegram(session, settings.telegram) if settings.telegram else None
        api = API(session, db, settings)
        bot = Bot(db, api, VK(session, settings), telegram, settings)

        bot.notifier.notify('🎉 Бот запускается…')
        api.prepare()
        bot.prepare()

        logger.info('Welcome «{}»!', bot.user.name)
        logger.info('Game time: {:%H:%M:%S %Z}', datetime.now(bot.user.tz))
        logger.info('Next day: {:%H:%M:%S %Z}.', bot.user.next_day.astimezone(bot.user.tz))
        bot.notifier.notify(f'🎉 Бот *{bot.user.name}* запущен!')

        if not shell:
            bot.run()
        else:
            IPython.embed()


if __name__ == '__main__':
    main(auto_envvar_prefix='BESTMOBABOT')
