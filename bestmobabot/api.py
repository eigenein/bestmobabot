import hashlib
import json
import random
import re
import string
from typing import Any, Callable, Dict, List, NamedTuple, NewType, Optional, TypeVar

import aiohttp

from bestmobabot.utils import logger


class UserInfo(NamedTuple):
    account_id: str
    name: str

    @staticmethod
    def parse(item: Dict) -> 'UserInfo':
        return UserInfo(
            account_id=item['accountId'],
            name=item['name'],
        )


class Reward(NamedTuple):
    consumable: Dict[str, int]

    @staticmethod
    def parse(item: Dict) -> 'Reward':
        return Reward(consumable=item['consumable'])


ExpeditionStatus = NewType('ExpeditionStatus', int)
ExpeditionStatus.COLLECT_REWARD = ExpeditionStatus(2)
ExpeditionStatus.FINISHED = ExpeditionStatus(3)


class Expedition(NamedTuple):
    id: int
    status: int

    @staticmethod
    def parse(item: Dict) -> 'Expedition':
        return Expedition(
            id=item['id'],
            status=ExpeditionStatus(item['status']),
        )


class ExpeditionFarmResult(NamedTuple):
    reward: Reward

    @staticmethod
    def parse(item: Dict) -> 'ExpeditionFarmResult':
        return ExpeditionFarmResult(reward=Reward.parse(item['reward']))


class Api:
    GAME_URL = 'https://vk.com/app5327745'
    IFRAME_URL = 'https://i-heroes-vk.nextersglobal.com/iframe/vkontakte/iframe.new.php'
    API_URL = 'https://heroes-vk.nextersglobal.com/api/'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'

    @staticmethod
    async def authenticate(remixsid: str) -> 'Api':
        logger.info('🔑 Authenticating…')

        async with aiohttp.ClientSession(cookies={'remixsid': remixsid}, raise_for_status=True) as session:
            logger.debug('🌎 Loading game page on VK.com…')
            async with await session.get(Api.GAME_URL, verify_ssl=False) as response:  # type: aiohttp.ClientResponse
                app_page = await response.text()

            # Look for params variable in the script.
            match = re.search(r'var params\s?=\s?({[^\}]+\})', app_page)
            assert match, 'params not found'
            params = json.loads(match.group(1))
            for key, value in params.items():
                logger.debug('🔡 %s: %s', key, value)

            # Load the proxy page and look for Hero Wars authentication token.
            logger.debug('🌎 Authenticating in Hero Wars…')
            async with session.get(Api.IFRAME_URL, params=params, verify_ssl=False) as response:  # type: aiohttp.ClientResponse
                iframe_new = await response.text()
            match = re.search(r'auth_key=([a-zA-Z0-9.\-]+)', iframe_new)
            assert match, f'authentication key is not found: {iframe_new}'
            auth_token = match.group(1)

            logger.info('🔑 Authentication token: %s', auth_token)
        return Api(auth_token, str(params['viewer_id']))

    def __init__(self, auth_token: str, user_id: str):
        self.auth_token = auth_token
        self.user_id = user_id
        self.request_id = 0
        self.session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(14))
        self.session = aiohttp.ClientSession(raise_for_status=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.session.__aexit__(exc_type, exc_val, exc_tb)

    def new_request_id(self) -> int:
        self.request_id += 1
        return self.request_id

    async def call(self, name: str, arguments: Optional[Dict[str, Any]] = None):
        request_id = str(self.new_request_id())
        logger.debug('🔔 #%s %s(%r)', request_id, name, arguments)

        calls = [{'ident': name, 'name': name, 'args': arguments or {}}]
        data = json.dumps({"session": None, "calls": calls})
        headers = {
            'User-Agent': self.USER_AGENT,
            'X-Auth-Application-Id': '5327745',
            'X-Auth-Network-Ident': 'vkontakte',
            'X-Auth-Session-Id': self.session_id,
            'X-Auth-Session-Key': '',
            'X-Auth-Token': self.auth_token,
            'X-Auth-User-Id': self.user_id,
            'X-Env-Library-Version': '1',
            'X-Env-Referrer': 'unknown',
            'X-Request-Id': request_id,
            'X-Requested-With': 'ShockwaveFlash / 28.0.0.126',
            'X-Server-Time': '0',
        }
        if self.request_id == 1:
            headers['X-Auth-Session-Init'] = '1'
        headers["X-Auth-Signature"] = self.sign_request(data, headers)

        async with self.session.post(self.API_URL, data=data, headers=headers, verify_ssl=False) as response:  # type: aiohttp.ClientResponse
            result = await response.json(content_type=None)
        if 'results' in result:
            return result['results'][0]['result']['response']
        if 'error' in result:
            return result['error']
        raise ValueError(result)

    @staticmethod
    def sign_request(data: str, headers: dict) -> str:
        fingerprint = ''.join(
            f'{key}={value}'
            for key, value in sorted(
                (key[6:].upper(), value)
                for key, value in headers.items()
                if key.startswith('X-Env')
            )
        )
        data = ':'.join((
            headers['X-Request-Id'],
            headers['X-Auth-Token'],
            headers['X-Auth-Session-Id'],
            data,
            fingerprint,
        )).encode('utf-8')
        return hashlib.md5(data).hexdigest()

    TNamedTuple = TypeVar('TNamedTuple')

    @staticmethod
    def parse_list(items: List[Dict], parse: Callable[[Dict], TNamedTuple]) -> List[TNamedTuple]:
        return [parse(item) for item in items]

    async def get_user_info(self) -> UserInfo:
        return UserInfo.parse(await self.call('userGetInfo'))

    async def list_expeditions(self) -> List[Expedition]:
        return self.parse_list(await self.call('expeditionGet'), Expedition.parse)

    async def farm_expedition(self, expedition_id: int) -> ExpeditionFarmResult:
        response = await self.call('expeditionFarm', {'expeditionId': expedition_id})
        return ExpeditionFarmResult.parse(response)

    async def farm_quest(self):
        # {calls: [{name: "questFarm", args: {questId: 10015}, ident: "body"}], session: null}
        # {"date":1514923436.037724,"results":[{"ident":"body","result":{"response":{"stamina":60}}}]}
        pass
