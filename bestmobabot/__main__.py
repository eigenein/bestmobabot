import asyncio
import logging

import click
import coloredlogs

from bestmobabot.api import Api
from bestmobabot.bot import Bot


@click.command()
@click.option('-s', '--remixsid', help='VK.com remixsid cookie.', required=True)
def main(remixsid: str):
    """
    Hero Wars bot.
    """
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level='DEBUG')
    logging.info('🤖 Bot is starting.')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(remixsid))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


async def async_main(remixsid: str):
    api = await Api.authenticate(remixsid)
    await Bot(api).run()


if __name__ == '__main__':
    main()
