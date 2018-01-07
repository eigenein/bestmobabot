from datetime import datetime
from typing import TextIO

import click
import coloredlogs

from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.utils import logger


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='BESTMOBABOT_REMIXSID', required=True)
@click.option('-v', '--verbose', help='Increase verbosity.', is_flag=True)
@click.option('-l', '--log-file', help='Log file.', envvar='BESTMOBABOT_LOGFILE', type=click.File('wt'), default=click.get_text_stream('stderr'))
def main(remixsid: str, verbose: True, log_file: TextIO):
    """
    Hero Wars bot.
    """
    level = 'DEBUG' if verbose else 'INFO'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=level, logger=logger, stream=log_file)
    logger.info('🤖 Bot is starting.')

    with API(remixsid) as api:
        api.authenticate()
        with Bot.start(api) as bot:
            logger.info(f'👋 Welcome {bot.user.name}!')
            logger.info(f'👋 Your local time is {datetime.now(bot.user.tz)}.')
            bot.run()


if __name__ == '__main__':
    main()
