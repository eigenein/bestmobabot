import asyncio

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

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(remixsid))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


async def async_main(remixsid: str):
    api = await Api.authenticate(remixsid)
    user_info = await api.get_user_info()
    logger.info(f'👋 Welcome {user_info.name}!')
    async with Bot(api) as bot:
        await bot.run()


if __name__ == '__main__':
    main()
