from datetime import datetime

import click
import coloredlogs

from bestmobabot.api import Api
from bestmobabot.bot import Bot
from bestmobabot.utils import logger


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', required=True)
@click.option('-v', '--verbose', help='Increase verbosity.', is_flag=True)
def main(remixsid: str, verbose: True):
    """
    Hero Wars bot.
    """
    level = 'DEBUG' if verbose else 'INFO'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=level, logger=logger)
    logger.info('🤖 Bot is starting.')

    with Api(remixsid) as api:
        api.authenticate()
        with Bot.start(api) as bot:
            logger.info(f'👋 Welcome {bot.user.name}!')
            logger.info(f'👋 Your local time is {datetime.now(bot.user.tz)}.')
            bot.run()


if __name__ == '__main__':
    main()
