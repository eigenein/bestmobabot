import click
import coloredlogs

from bestmobabot.api import Api
from bestmobabot.bot import Bot
from bestmobabot.utils import logger


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', required=True)
def main(remixsid: str):
    """
    Hero Wars bot.
    """
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level='DEBUG', logger=logger)
    logger.info('🤖 Bot is starting.')

    with Api.authenticate(remixsid) as api:
        user_info = api.get_user_info()
        logger.info(f'👋 Welcome {user_info.name}!')
        with Bot(api) as bot:
            bot.run()


if __name__ == '__main__':
    main()
