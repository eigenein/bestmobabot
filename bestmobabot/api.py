import logging

import aiohttp


class Api:
    URL = 'https://heroes-vk.nextersglobal.com/api/'

    @staticmethod
    async def authenticate(remixsid: str) -> 'Api':
        logging.info('🔑 Authenticating…')
        pass  # TODO: https://github.com/eigenein/epicwar/blob/master/epicbot/api.py#L181

    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.request_id = 0

    def new_request_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def call(self):
        pass  # TODO: https://github.com/eigenein/epicwar/blob/master/epicbot/api.py#L584

    async def quest_farm(self):
        # {calls: [{name: "questFarm", args: {questId: 10015}, ident: "body"}], session: null}
        # {"date":1514923436.037724,"results":[{"ident":"body","result":{"response":{"stamina":60}}}]}
        pass
