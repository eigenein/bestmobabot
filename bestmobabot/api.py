import contextlib
import hashlib
import json
import random
import re
import string
from time import sleep
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from bestmobabot import responses, types
from bestmobabot.utils import logger


class ApiError(Exception):
    def __init__(self, name: Optional[str], description: Optional[str]):
        super().__init__(name, description)
        self.name = name
        self.description = description


class AlreadyError(ApiError):
    pass


class InvalidSessionError(ApiError):
    pass


class NotEnoughError(ApiError):
    pass


class NotAvailableError(ApiError):
    pass


class InvalidResponseError(ValueError):
    pass


class Api(contextlib.AbstractContextManager):
    GAME_URL = 'https://vk.com/app5327745'
    IFRAME_URL = 'https://i-heroes-vk.nextersglobal.com/iframe/vkontakte/iframe.new.php'
    API_URL = 'https://heroes-vk.nextersglobal.com/api/'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'

    def __init__(self, remixsid: str):
        self.remixsid = remixsid
        self.auth_token: str = None
        self.user_id: str = None
        self.request_id: int = None
        self.session_id: str = None
        self.session = requests.Session()

        # Store last API results for debugging.
        self.last_responses: List[str] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)

    def authenticate(self):
        logger.info('🔑 Authenticating…')

        with requests.Session() as session:
            logger.debug('🌎 Loading game page on VK.com…')
            with session.get(Api.GAME_URL, cookies={'remixsid': self.remixsid}) as response:
                response.raise_for_status()
                app_page = response.text

            # Look for params variable in the script.
            match = re.search(r'var params\s?=\s?({[^\}]+\})', app_page)
            assert match, 'params not found'
            params = json.loads(match.group(1))
            for key, value in params.items():
                logger.debug('🔡 %s: %s', key, value)

            # Load the proxy page and look for Hero Wars authentication token.
            logger.debug('🌎 Authenticating in Hero Wars…')
            with session.get(Api.IFRAME_URL, params=params) as response:
                response.raise_for_status()
                iframe_new = response.text
            match = re.search(r'auth_key=([a-zA-Z0-9.\-]+)', iframe_new)
            assert match, f'authentication key is not found: {iframe_new}'
            self.auth_token = match.group(1)

        logger.info('🔑 Authentication token: %s', self.auth_token)
        self.user_id = str(params['viewer_id'])
        self.request_id = 0
        self.session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(14))

    def new_request_id(self) -> int:
        self.request_id += 1
        return self.request_id

    def call(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> responses.Response:
        request_id = str(self.new_request_id())
        logger.info('🔔 #%s %s(%r)', request_id, name, arguments or {})

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

        if self.request_id != 1:
            # Emulate human behavior a little bit.
            sleep(random.uniform(5.0, 15.0))

        with self.session.post(self.API_URL, data=data, headers=headers) as response:
            self.last_responses.append(response.text)
            response.raise_for_status()
            try:
                result = response.json()
            except ValueError as e:
                result = {}  # just for PyCharm
                raise InvalidResponseError(response.text) from e

        if 'results' in result:
            return responses.Response.parse(result['results'][0]['result'])
        if 'error' in result:
            raise self.make_exception(result['error'])
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

    exception_classes = {
        'Already': AlreadyError,
        'common\\rpc\\exception\\InvalidSession': InvalidSessionError,
        'NotEnough': NotEnoughError,
        'NotAvailable': NotAvailableError,
    }

    @classmethod
    def make_exception(cls, error: Dict) -> 'ApiError':
        name = error.get('name')
        description = error.get('description')
        return cls.exception_classes.get(name, ApiError)(name, description)

    def get_user_info(self) -> responses.User:
        return responses.User.parse(self.call('userGetInfo').payload)

    def farm_daily_bonus(self) -> responses.Reward:
        return responses.Reward.parse(self.call('dailyBonusFarm', {'vip': 0}).payload)

    def list_expeditions(self) -> List[responses.Expedition]:
        return list(map(responses.Expedition.parse, self.call('expeditionGet')))

    def farm_expedition(self, expedition_id: types.ExpeditionID) -> responses.Reward:
        return responses.Reward.parse(self.call('expeditionFarm', {'expeditionId': expedition_id}).payload)

    def get_all_quests(self) -> responses.Quests:
        return list(map(responses.Quest.parse, self.call('questGetAll').payload))

    def farm_quest(self, quest_id: types.QuestID) -> responses.Reward:
        return responses.Reward.parse(self.call('questFarm', {'questId': quest_id}).payload)

    def get_all_mail(self) -> List[responses.Letter]:
        return list(map(responses.Letter.parse, self.call('mailGetAll').payload['letters']))

    def farm_mail(self, letter_ids: Iterable[responses.LetterID]) -> Dict[str, responses.Reward]:
        response = self.call('mailFarm', {'letterIds': list(letter_ids)})
        return {letter_id: responses.Reward.parse(item or {}) for letter_id, item in response.payload.items()}

    def buy_chest(self, is_free=True, chest='town', is_pack=False) -> List[responses.Reward]:
        response = self.call('chestBuy', {'free': is_free, 'chest': chest, 'pack': is_pack})
        return list(map(responses.Reward.parse, response.payload['rewards']))

    def send_daily_gift(self, ids: Iterable[types.UserID]) -> responses.Quests:
        return self.call('friendsSendDailyGift', {'ids': list(ids)}).quests

    def find_arena_enemies(self) -> List[responses.ArenaEnemy]:
        return list(map(responses.ArenaEnemy.parse, self.call('arenaFindEnemies').payload))

    def attack_arena(self, user_id: types.UserID, hero_ids: Iterable[types.HeroID]) -> Tuple[responses.ArenaResult, responses.Quests]:
        response = self.call('arenaAttack', {'userId': user_id, 'heroes': list(hero_ids)})
        return responses.ArenaResult.parse(response.payload), response.quests

    def get_all_heroes(self) -> List[responses.Hero]:
        return list(map(responses.Hero.parse, self.call('heroGetAll').payload.values()))

    def check_freebie(self, gift_id: str) -> Optional[responses.Reward]:
        response = self.call('freebieCheck', {'giftId': gift_id}).payload
        return responses.Reward.parse(response) if response else None

    def farm_zeppelin_gift(self) -> responses.Reward:
        return responses.Reward.parse(self.call('zeppelinGiftFarm').payload)

    def open_artifact_chest(self, amount=1, is_free=True) -> List[responses.Reward]:
        payload = self.call('artifactChestOpen', {'amount': amount, 'free': is_free}).payload
        return list(map(responses.Reward.parse, payload['chestReward']))
