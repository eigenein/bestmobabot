"""
Game API response wrappers.
"""

from abc import ABC, ABCMeta
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar

import numpy
from loguru import logger

from bestmobabot import constants, resources
from bestmobabot.dataclasses_ import Reward

T1 = TypeVar('T1')
T2 = TypeVar('T2')


class BaseResponse(ABC):
    """
    Base for all response classes.
    """

    def __init__(self, raw: Dict):
        self.raw = raw


class Result(BaseResponse):
    """
    Top-most result class.
    """

    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.response: Any = raw['response']
        self.quests: 'Quests' = [Quest(quest) for quest in raw.get('quests', [])]


class User(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.name: str = raw['name']
        self.tz: tzinfo = timezone(timedelta(hours=raw.get('timeZone', 0)))
        self.clan_id: Optional[str] = cast_optional(raw.get('clanId'), str)
        self.clan_title: Optional[str] = raw.get('clanTitle')
        self.next_day: datetime = datetime.fromtimestamp(raw.get('nextDayTs', 0), self.tz)
        self.server_id: str = raw['serverId']
        self.level: str = raw['level']
        self.star_money: Optional[str] = raw.get('starMoney')
        self.gold: Optional[str] = raw.get('gold')

    def is_from_clans(self, clans: Iterable[str]) -> bool:
        return (self.clan_id and self.clan_id in clans) or (self.clan_title and self.clan_title in clans)


class Expedition(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.status: int = int(raw['status'])
        self.end_time: Optional[datetime] = datetime.fromtimestamp(raw['endTime']).astimezone() if raw.get('endTime') else None  # noqa
        self.power: int = int(raw['power'])
        self.duration: timedelta = timedelta(seconds=raw['duration'])
        self.hero_ids: List[str] = [str(hero_id) for hero_id in raw.get('heroes', [])]

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Quest(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.state: int = int(raw['state'])
        self.progress: int = int(raw['progress'])
        self.reward: Reward = Reward.parse_obj(raw['reward'])

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


Quests = List[Quest]


class Hero(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.level: int = int(raw['level'])
        self.color: int = int(raw['color'])
        self.star: int = int(raw['star'])
        self.power: Optional[int] = cast_optional(raw.get('power'), int)

        # Should be here to optimise performance.
        self.feature_dict = {
            f'color_{self.id}': float(self.color),
            f'level_{self.id}': float(self.level),
            f'star_{self.id}': float(self.star),
            f'color_level_star_{self.id}': float(self.color) * float(self.level) * float(self.star),
            f'color_level_{self.id}': float(self.color) * float(self.level),
            f'color_star_{self.id}': float(self.color) * float(self.star),
            f'level_star_{self.id}': float(self.level) * float(self.star),
            'total_color_level_star': float(self.color) * float(self.level) * float(self.star),
            'total_color_level': float(self.color) * float(self.level),
            'total_color_star': float(self.color) * float(self.star),
            'total_level_star': float(self.level) * float(self.star),
            'total_colors': float(self.color),
            'total_levels': float(self.level),
            'total_stars': float(self.star),
            'total_heroes': 1.0,
        }

    def get_features(self, model) -> numpy.ndarray:
        """
        Construct hero features for prediction model.
        """
        # noinspection PyUnresolvedReferences
        return numpy.fromiter((self.feature_dict.get(name, 0.0) for name in model.feature_names), numpy.float)

    def dump(self) -> dict:
        return {key: self.raw[key] for key in ('id', 'level', 'color', 'star', 'power')}

    def order(self):
        """
        Get comparison order.
        """
        return self.star, self.color, self.level

    def __str__(self):
        return f'{"⭐" * self.star} {resources.hero_name(self.id)} ({self.level}) {constants.COLORS.get(self.color, self.color)}'  # noqa


class BaseArenaEnemy(BaseResponse, metaclass=ABCMeta):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.user_id: str = str(raw['userId'])
        self.place: str = str(raw['place'])
        self.power: int = int(raw['power'])
        self.user: Optional[User] = cast_optional(raw.get('user'), User)


class ArenaEnemy(BaseArenaEnemy):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.heroes: List[Hero] = [Hero(hero) for hero in raw['heroes']]


class GrandArenaEnemy(BaseArenaEnemy):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.heroes: List[List[Hero]] = [[Hero(hero) for hero in heroes] for heroes in raw['heroes']]


class ArenaResult(BaseResponse):
    """
    Unified arena result for normal arena and grand arena.
    """

    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.win: bool = raw['win']
        self.arena_place: Optional[str] = cast_optional(raw['state'].get('arenaPlace'), str)
        self.grand_place: Optional[str] = cast_optional(raw['state'].get('grandPlace'), str)
        self.battles: List['BattleResult'] = [BattleResult(result) for result in raw['battles']]
        self.reward: Reward = Reward.parse_obj(raw['reward'] or {})

    def log(self):
        logger.info('You won!' if self.win else 'You lose.')
        for i, battle in enumerate(self.battles, start=1):
            logger.info(f'Battle #{i}: {"⭐" * battle.stars if battle.win else "lose."}')
        self.reward.log()


class BattleResult(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.win: bool = raw['result']['win']
        self.stars: int = int(raw['result'].get('stars', 0))


class Boss(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.may_raid: bool = raw['mayRaid']


class Battle(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.seed: int = raw['seed']


class Replay(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.start_time: datetime = datetime.fromtimestamp(int(raw['startTime']))
        self.win: bool = raw['result']['win']
        self.stars: int = int(raw['result']['stars'])
        self.attackers: List[Hero] = [Hero(hero) for hero in raw['attackers'].values()]
        self.defenders: List[List[Hero]] = [
            [Hero(hero) for hero in defenders.values()]
            for defenders in raw['defenders']
        ]


class ShopSlot(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.is_bought: bool = bool(raw['bought'])
        self.reward: Reward = Reward.parse_obj(raw['reward'])
        self.costs_star_money: bool = bool(raw['cost'].get('starmoney', 0))


class Tower(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.floor_number = int(raw['floorNumber'])
        self.may_skip_floor = int(raw['maySkipFloor'])
        self.floor_type = raw['floorType'].lower()
        # This is only available on a buff floor.
        self.buff_ids: List[int] = [int(buff['id']) for buff in raw['floor']] if self.is_buff else []

    @property
    def is_battle(self) -> bool:
        return self.floor_type == 'battle'

    @property
    def is_buff(self) -> bool:
        return self.floor_type == 'buff'

    @property
    def is_chest(self):
        return self.floor_type == 'chest'


class Mission(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id = str(raw['id'])
        self.tries_spent = int(raw['triesSpent'])
        self.stars = int(raw['stars'])

    @property
    def is_raid_available(self) -> bool:
        return self.stars == constants.RAID_N_STARS


class Offer(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id = str(raw['id'])
        self.is_free_reward_obtained: bool = raw.get('freeRewardObtained', False)
        self.offer_type: str = raw.get('offerType', '')


def cast_optional(value: Optional[T1], cast: Callable[[T1], T2]) -> Optional[T2]:
    return cast(value) if value is not None else None
