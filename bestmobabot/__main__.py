import json
from datetime import datetime
from pathlib import Path
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

    state_path = Path(f'remixsid-{remixsid}.json')

    with API(remixsid) as api:
        # Try to read cached state.
        logger.info('🔑 Checking saved state in %s…', state_path)
        state = json.loads(state_path.read_text()) if state_path.is_file() else None
        # Start the bot.
        api.start(state)
        with Bot(api) as bot:
            bot.start(state)
            logger.info(f'👋 Welcome {bot.user.name}! Your local time is {datetime.now(bot.user.tz)}.')
            try:
                bot.run()
            except KeyboardInterrupt:
                # Cache user ID and authentication token for faster restart.
                logger.info('🔑 Writing state to %s…', state_path)
                state_path.write_text(json.dumps({**api.state, **bot.state}, indent=2))
                raise


if __name__ == '__main__':
    main()
