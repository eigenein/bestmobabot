from bestmobabot.api import Api
from bestmobabot.utils import logger


class Bot:
    def __init__(self, api: Api):
        self.api = api

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.api.__aexit__(exc_type, exc_val, exc_tb)

    async def run(self):
        logger.info('🤖 Running.')
