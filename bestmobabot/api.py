"""
Game API wrapper.
"""

import contextlib
import hashlib
import random
import re
import string
from datetime import datetime
from time import sleep, time
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar

import orjson
import requests
from loguru import logger
from requests.adapters import HTTPAdapter

from bestmobabot import constants
from bestmobabot.database import Database
from bestmobabot.dataclasses_ import (
    ArenaEnemy,
    ArenaResult,
    Boss,
    Expedition,
    GrandArenaEnemy,
    Hero,
    Letter,
    Mission,
    Offer,
    Quest,
    Quests,
    Replay,
    Result,
    Reward,
    ShopSlot,
    Tower,
    User,
)
from bestmobabot.enums import BattleType
from bestmobabot.settings import Settings
from bestmobabot.tracking import send_event

T = TypeVar('T')


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


class NotFoundError(ApiError):
    pass


class ArgumentError(ApiError):
    pass


class OutOfRetargetDelta(Exception):
    pass


class ResponseError(ValueError):
    pass


class InvalidResponseError(ResponseError):
    pass


class InvalidSignatureError(ResponseError):
    pass


class API(contextlib.AbstractContextManager):
    GAME_URL = 'https://vk.com/app5327745'
    IFRAME_URL = 'https://i-heroes-vk.nextersglobal.com/iframe/vkontakte/iframe.new.php'
    API_URL = 'https://heroes-vk.nextersglobal.com/api/'

    def __init__(self, db: Database, settings: Settings):
        self.db = db
        self.remixsid = settings.vk.remixsid
        self.auth_token: str = None
        self.user_id: str = None
        self.request_id: int = None
        self.session_id: str = None
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=5))

        # Store last API results for debugging.
        self.last_responses: List[str] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)

    def start(self, invalidate_session: bool = False):
        if not invalidate_session:
            try:
                state: Dict[str, Any] = self.db[f'api:{self.remixsid}:state']
            except KeyError:
                logger.info('Previously saved state is missing.')
            else:
                logger.info('Using saved credentials.')
                self.user_id = state['user_id']
                self.auth_token = state['auth_token']
                self.session_id = state['session_id']
                try:
                    self.request_id = self.db[f'api:{self.remixsid}:request_id']
                except KeyError:
                    self.request_id = 0
                return

        logger.info('Authenticating…')
        with requests.Session() as session:
            logger.debug('Loading game page on VK.com…')
            with session.get(
                API.GAME_URL,
                cookies={'remixsid': self.remixsid},
                timeout=constants.API_TIMEOUT,
            ) as response:
                logger.info('Status: {}.', response.status_code)
                response.raise_for_status()
                app_page = response.text

            # Look for params variable in the script.
            match = re.search(r'var params\s?=\s?({[^\}]+\})', app_page)
            assert match, 'params not found'
            params = orjson.loads(match.group(1))
            logger.trace('params: {}', params)

            # Load the proxy page and look for Hero Wars authentication token.
            logger.debug('Authenticating in Hero Wars…')
            with session.get(API.IFRAME_URL, params=params, timeout=constants.API_TIMEOUT) as response:
                logger.info('Status: {}.', response.status_code)
                response.raise_for_status()
                iframe_new = response.text
            match = re.search(r'auth_key=([a-zA-Z0-9.\-]+)', iframe_new)
            assert match, f'authentication key is not found: {iframe_new}'
            self.auth_token = match.group(1)

        logger.debug('Authentication token: {}', self.auth_token)
        self.user_id = str(params['viewer_id'])
        self.session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(14))
        self.request_id = 0

        self.db[f'api:{self.remixsid}:state'] = {
            'user_id': self.user_id,
            'auth_token': self.auth_token,
            'session_id': self.session_id,
        }

    def call(self, name: str, arguments: Optional[Dict[str, Any]] = None, random_sleep=True) -> Result:
        try:
            return self._call(name, arguments=arguments, random_sleep=random_sleep)
        except (InvalidSessionError, InvalidSignatureError) as e:
            logger.warning('Invalid session: {}.', e)
            self.start(invalidate_session=True)
            logger.info('Retrying the call…')
            return self._call(name, arguments=arguments, random_sleep=random_sleep)

    def _call(self, name: str, *, arguments: Optional[Dict[str, Any]] = None, random_sleep=True) -> Result:
        self.request_id += 1
        self.db[f'api:{self.remixsid}:request_id'] = self.request_id

        # Emulate human behavior a little bit.
        sleep_time = random.uniform(5.0, 10.0) if random_sleep and self.request_id != 1 else 0.0
        logger.info(f'#{self.request_id}: {name}({arguments or {}}) in {sleep_time:.1f} seconds…')
        sleep(sleep_time)

        send_event(category='api', action=name, user_id=self.user_id)

        calls = [{'ident': name, 'name': name, 'args': arguments or {}}]
        data = orjson.dumps({"session": None, "calls": calls}).decode()
        headers = {
            'User-Agent': constants.USER_AGENT,
            'X-Auth-Application-Id': '5327745',
            'X-Auth-Network-Ident': 'vkontakte',
            'X-Auth-Session-Id': self.session_id,
            'X-Auth-Session-Key': '',
            'X-Auth-Token': self.auth_token,
            'X-Auth-User-Id': self.user_id,
            'X-Env-Library-Version': '1',
            'X-Env-Referrer': 'unknown',
            'X-Request-Id': str(self.request_id),
            'X-Requested-With': 'XMLHttpRequest',
            'X-Server-Time': f'{time():.3f}',
        }
        if self.request_id == 1:
            headers['X-Auth-Session-Init'] = '1'
        headers["X-Auth-Signature"] = self.sign_request(data, headers)

        # API developers are very funny people…
        # They return errors in a bunch of different ways. 🤦

        with self.session.post(self.API_URL, data=data, headers=headers, timeout=constants.API_TIMEOUT) as response:
            self.last_responses.append(response.text.strip())
            logger.info(f'#{self.request_id}: status {response.status_code}.')
            response.raise_for_status()
            try:
                item = response.json()
            except ValueError:
                if response.text == 'Invalid signature':
                    raise InvalidSignatureError(response.text)
                raise InvalidResponseError(response.text)

        if 'results' in item:
            result = Result.parse_obj(item['results'][0]['result'])
            if result.is_error:
                if result.response['error'] == 'outOfRetargetDelta':
                    raise OutOfRetargetDelta()
                raise ResponseError(result.response)
            return result
        if 'error' in item:
            raise self.make_exception(item['error'])
        raise ValueError(item)

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
        'NotFound': NotFoundError,
        'ArgumentError': ArgumentError,
    }

    @classmethod
    def make_exception(cls, error: Dict) -> 'ApiError':
        name = error.get('name')
        description = error.get('description')
        return cls.exception_classes.get(name, ApiError)(name, description)

    # User.
    # ------------------------------------------------------------------------------------------------------------------

    def register(self):
        self.call('registration', {'user': {'referrer': {'type': 'menu', 'id': '0'}}})

    def get_user_info(self) -> User:
        return User.parse_obj(self.call('userGetInfo').response)

    def get_all_heroes(self, random_sleep=True) -> List[Hero]:
        return list_of(Hero.parse_obj, self.call('heroGetAll', random_sleep=random_sleep).response)

    # Daily bonus.
    # ------------------------------------------------------------------------------------------------------------------

    def farm_daily_bonus(self) -> Reward:
        return Reward.parse_obj(self.call('dailyBonusFarm', {'vip': 0}).response)

    # Expeditions.
    # ------------------------------------------------------------------------------------------------------------------

    def list_expeditions(self) -> List[Expedition]:
        return list_of(Expedition.parse_obj, self.call('expeditionGet').response)

    def farm_expedition(self, expedition_id: str) -> Reward:
        return Reward.parse_obj(self.call('expeditionFarm', {'expeditionId': expedition_id}).response)

    def send_expedition_heroes(self, expedition_id: str, hero_ids: List[str]) -> Tuple[datetime, Quests]:
        response = self.call('expeditionSendHeroes', {'expeditionId': expedition_id, 'heroes': hero_ids})
        return datetime.fromtimestamp(response.response['endTime']).astimezone(), response.quests

    # Quests.
    # ------------------------------------------------------------------------------------------------------------------

    def get_all_quests(self) -> Quests:
        return list_of(Quest.parse_obj, self.call('questGetAll').response)

    def farm_quest(self, quest_id: str) -> Reward:
        return Reward.parse_obj(self.call('questFarm', {'questId': quest_id}).response)

    # Mail.
    # ------------------------------------------------------------------------------------------------------------------

    def get_all_mail(self) -> List[Letter]:
        return list_of(Letter.parse_obj, self.call('mailGetAll').response['letters'])

    def farm_mail(self, letter_ids: Iterable[str]) -> Dict[str, Reward]:
        result = self.call('mailFarm', {'letterIds': list(letter_ids)})
        return {letter_id: Reward.parse_obj(item or {}) for letter_id, item in result.response.items()}

    # Chests.
    # ------------------------------------------------------------------------------------------------------------------

    def buy_chest(self, is_free=True, chest='town', is_pack=False) -> List[Reward]:
        result = self.call('chestBuy', {'free': is_free, 'chest': chest, 'pack': is_pack})
        return list_of(Reward.parse_obj, result.response['rewards'])

    # Daily gift.
    # ------------------------------------------------------------------------------------------------------------------

    def send_daily_gift(self, user_ids: Iterable[str]) -> Quests:
        return self.call('friendsSendDailyGift', {'ids': list(user_ids), 'notifiedUserIds': []}).quests

    # Arena.
    # ------------------------------------------------------------------------------------------------------------------

    def find_arena_enemies(self) -> List[ArenaEnemy]:
        return list_of(ArenaEnemy.parse_obj, self.call('arenaFindEnemies').response)

    def attack_arena(self, user_id: str, hero_ids: Iterable[str]) -> Tuple[ArenaResult, Quests]:
        result = self.call('arenaAttack', {'userId': user_id, 'heroes': list(hero_ids)})
        return ArenaResult.parse_obj(result.response), result.quests

    def find_grand_enemies(self) -> List[GrandArenaEnemy]:
        # Random sleep is turned off because model prediction takes some time already.
        return list_of(GrandArenaEnemy.parse_obj, self.call('grandFindEnemies', random_sleep=False).response)

    def attack_grand(self, user_id: str, hero_ids: List[List[str]]) -> Tuple[ArenaResult, Quests]:
        result = self.call('grandAttack', {'userId': user_id, 'heroes': hero_ids})
        return ArenaResult.parse_obj(result.response), result.quests

    def farm_grand_coins(self) -> Reward:
        return Reward.parse_obj(self.call('grandFarmCoins').response['reward'] or {})

    def set_grand_heroes(self, hero_ids: List[List[str]]):
        self.call('grandSetHeroes', {'heroes': hero_ids})

    # Freebie.
    # ------------------------------------------------------------------------------------------------------------------

    def check_freebie(self, gift_id: str) -> Optional[Reward]:
        response = self.call('freebieCheck', {'giftId': gift_id}).response
        return Reward.parse_obj(response) if response else None

    # Zeppelin gift.
    # ------------------------------------------------------------------------------------------------------------------

    def farm_zeppelin_gift(self) -> Reward:
        return Reward.parse_obj(self.call('zeppelinGiftFarm').response)

    # Artifact chests.
    # ------------------------------------------------------------------------------------------------------------------

    def open_artifact_chest(self, amount=1, is_free=True) -> List[Reward]:
        response = self.call('artifactChestOpen', {'amount': amount, 'free': is_free}).response
        return list_of(Reward.parse_obj, response['chestReward'])

    # Battles.
    # ------------------------------------------------------------------------------------------------------------------

    def get_battle_by_type(self, battle_type: BattleType, offset=0, limit=20) -> List[Replay]:
        response = self.call('battleGetByType', {'type': battle_type.value, 'offset': offset, 'limit': limit}).response
        return list_of(Replay.parse_obj, response['replays'])

    # Raids.
    # https://github.com/eigenein/bestmobabot/wiki/Raids
    # ------------------------------------------------------------------------------------------------------------------

    def raid_mission(self, mission_id: str, times=1) -> List[Reward]:
        response = self.call('missionRaid', {'times': times, 'id': mission_id}).response
        return list_of(Reward.parse_obj, response)

    def get_all_missions(self) -> List[Mission]:
        return list_of(Mission.parse_obj, self.call('missionGetAll').response)

    # Boss.
    # https://github.com/eigenein/bestmobabot/wiki/Boss
    # ------------------------------------------------------------------------------------------------------------------

    def get_all_bosses(self) -> List[Boss]:
        return list_of(Boss.parse_obj, self.call('bossGetAll').response)

    def raid_boss(self, boss_id: str) -> Reward:
        return Reward.parse_obj(self.call('bossRaid', {'bossId': boss_id}).response['everyWinReward'])

    def open_boss_chest(self, boss_id: str) -> Tuple[List[Reward], Quests]:
        result = self.call('bossOpenChest', {'bossId': boss_id, 'starmoney': 0, 'amount': 1})
        return list_of(Reward.parse_obj, result.response['rewards']['free']), result.quests

    # Shop.
    # ------------------------------------------------------------------------------------------------------------------

    def get_shop(self, shop_id: str) -> List[ShopSlot]:
        response = self.call('shopGet', {'shopId': shop_id}).response
        return list_of(ShopSlot.parse_obj, response['slots'])

    def shop(self, *, slot_id: str, shop_id: str) -> Reward:
        return Reward.parse_obj(self.call('shopBuy', {'slot': slot_id, 'shopId': shop_id}).response)

    # Tower.
    # ------------------------------------------------------------------------------------------------------------------

    def get_tower_info(self) -> Tower:
        return Tower.parse_obj(self.call('towerGetInfo').response)

    def skip_tower_floor(self) -> Tuple[Tower, Reward]:
        response = self.call('towerSkipFloor').response
        return Tower.parse_obj(response['tower']), Reward.parse_obj(response['reward'])

    def buy_tower_buff(self, buff_id: int) -> Tower:
        return Tower.parse_obj(self.call('towerBuyBuff', {'buffId': buff_id}).response)

    def open_tower_chest(self, number: int) -> Tuple[Reward, Quests]:
        assert number in (0, 1, 2)
        result = self.call('towerOpenChest', {'num': number})
        return Reward.parse_obj(result.response['reward']), result.quests

    def next_tower_floor(self) -> Tower:
        return Tower.parse_obj(self.call('towerNextFloor').response)

    def next_tower_chest(self) -> Tower:
        return Tower.parse_obj(self.call('towerNextChest').response)

    def start_tower_battle(self, hero_ids: Iterable[str]) -> Any:
        return self.call('towerStartBattle', {'heroes': hero_ids}).response

    def end_tower_battle(self, arguments: Dict[str, Any]) -> Reward:
        return Reward.parse_obj(self.call('towerEndBattle', arguments).response['reward'])

    # Offers.
    # ------------------------------------------------------------------------------------------------------------------

    def get_all_offers(self) -> List[Offer]:
        return list_of(Offer.parse_obj, self.call('offerGetAll').response)

    def farm_offer_reward(self, offer_id: str) -> Reward:
        return Reward.parse_obj(self.call('offerFarmReward', {'offerId': offer_id}).response)

    # Titans.
    # ------------------------------------------------------------------------------------------------------------------

    def open_titan_artifact_chest(self, amount: int, free: bool = True) -> Tuple[List[Reward], Quests]:
        result = self.call('titanArtifactChestOpen', {'amount': amount, 'free': free})
        return list_of(Reward.parse_obj, result.response['reward']), result.quests

    # Runes.
    # ------------------------------------------------------------------------------------------------------------------

    def enchant_hero_rune(
        self,
        hero_id: str,
        tier: str,
        consumables: Optional[Dict[str, int]] = None,
    ) -> Result:
        return self.call('heroEnchantRune', {
            'heroId': hero_id,
            'tier': tier,
            'items': {'consumable': consumables or {'1': 1}}},
        )


def list_of(constructor: Callable[[Any], T], items: Iterable) -> List[T]:
    """
    Used to protect from changing a response from list to dictionary and vice versa.
    This often happens with the game updates.
    """
    # FIXME: accept `BaseModel` subclasses instead of `constructor`.
    if isinstance(items, dict):
        # Equally treat lists and dictionaries. Because there're two possibilities in the responses:
        # 1. `[{"id": "1", ...}]`
        # 2. `{"1": {"id": "1"}, ...}`
        items = items.values()
    return [constructor(item) for item in items]
