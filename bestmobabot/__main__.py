import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, TextIO

import click
import coloredlogs

from bestmobabot.api import API
from bestmobabot.bot import Bot
from bestmobabot.logger import logger


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', envvar='BESTMOBABOT_REMIXSID', required=True)
@click.option('--no-experience', help='Do not farm experience.', envvar='BESTMOBABOT_NO_EXPERIENCE', is_flag=True)
@click.option('-v', '--verbose', help='Increase verbosity.', is_flag=True)
@click.option('-l', '--log-file', help='Log file.', envvar='BESTMOBABOT_LOGFILE', type=click.File('wt'), default=click.get_text_stream('stderr'))
def main(remixsid: str, no_experience: bool, verbose: bool, log_file: TextIO):
    """
    Hero Wars bot.
    """
    level = 'DEBUG' if verbose else 'INFO'
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=level, logger=logger, stream=log_file)
    logger.info('🤖 Bot is starting.')

    with API(remixsid) as api:
        # Try to read cached state.
        state_path = Path(f'remixsid-{remixsid}.json')
        state = read_state(state_path)
        # Start the bot.
        api.start(state)
        with Bot(api, no_experience) as bot:
            bot.start(state)
            logger.info(f'👋 Welcome {bot.user.name}! Your game time is {datetime.now(bot.user.tz):%H:%M:%S}.')
            try:
                bot.run()
            except KeyboardInterrupt:
                # Save the state for faster restart.
                logger.info('🔑 Writing state to %s…', state_path)
                state_path.write_text(json.dumps({
                    'datetime': datetime.now().timestamp(),
                    **api.state,
                    **bot.state,
                }, indent=2))
                raise


def read_state(path: Path) -> Optional[Dict]:
    if not path.is_file():
        logger.info('😐 No saved state found.')
        return None
    logger.info('😀 Reading saved state from %s…', path)
    state = json.loads(path.read_text())
    if datetime.now() - datetime.fromtimestamp(state['datetime']) > timedelta(days=1):
        logger.warning('😐 Saved state is too old.')
        return None
    return state


if __name__ == '__main__':
    main()
