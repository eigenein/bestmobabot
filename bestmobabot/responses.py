"""
Game API response wrappers.
"""

import logging
from abc import ABC, ABCMeta
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Dict, List, Optional

import numpy

import bestmobabot.model
from bestmobabot import constants
from bestmobabot.resources import artifact_name, coin_name, consumable_name, gear_name, hero_name, scroll_name


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
        self.clan_id: Optional[str] = raw.get('clanId')
        self.next_day: datetime = datetime.fromtimestamp(raw.get('nextDayTs', 0), self.tz)

    def is_from_clan(self, clan_id: Optional[str]) -> bool:
        return clan_id and self.clan_id and self.clan_id == clan_id


class Expedition(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.status: int = int(raw['status'])
        self.end_time: Optional[datetime] = datetime.fromtimestamp(raw['endTime']).astimezone() if raw.get('endTime') else None
        self.power: int = int(raw['power'])
        self.duration: timedelta = timedelta(seconds=raw['duration'])
        self.hero_ids: List[str] = [str(hero_id) for hero_id in raw.get('heroes', [])]

    @property
    def is_available(self) -> bool:
        return self.status == 1

    @property
    def is_started(self) -> bool:
        return self.status == 2


class Reward(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.stamina: int = int(raw.get('stamina', 0))
        self.gold: int = int(raw.get('gold', 0))
        self.experience: int = int(raw.get('experience', 0))
        self.consumable: Dict[str, int] = raw.get('consumable', {})
        self.star_money: int = int(raw.get('starmoney', 0))
        self.coin: Dict[str, str] = raw.get('coin', {})
        self.hero_fragment: Dict[str, int] = raw.get('fragmentHero', {})
        self.artifact_fragment: Dict[str, int] = raw.get('fragmentArtifact', {})
        self.gear_fragment: Dict[str, int] = raw.get('fragmentGear', {})
        self.gear: Dict[str, str] = raw.get('gear', {})
        self.scroll_fragment: Dict[str, str] = raw.get('fragmentScroll', {})
        self.tower_point = int(raw.get('towerPoint', 0))

    def log(self, logger: logging.Logger):
        if self.stamina:
            logger.info(f'🔋 {self.stamina} × stamina.')
        if self.gold:
            logger.info(f'💰 {self.gold} × gold.')
        if self.experience:
            logger.info(f'📈 {self.experience} × experience.')
        for consumable_id, value in self.consumable.items():
            logger.info(f'🍔 {value} × «{consumable_name(consumable_id)}» consumable.')
        if self.star_money:
            logger.info(f'✨ {self.star_money} × star money.')
        for coin_id, value in self.coin.items():
            logger.info(f'💟️ {value} × «{coin_name(coin_id)}» coin.')
        for hero_id, value in self.hero_fragment.items():
            logger.info(f'🔮 {value} × «{hero_name(hero_id)}» hero fragment.')
        for artifact_id, value in self.artifact_fragment.items():
            logger.info(f'👕 {value} × «{artifact_name(artifact_id)}» artifact fragment.')
        for gear_id, value in self.gear_fragment.items():
            logger.info(f'👕 {value} × «{gear_name(gear_id)}» gear fragment.')
        for gear_id, value in self.gear.items():
            logger.info(f'👕 {value} × «{gear_name(gear_id)}» gear.')
        for scroll_id, value in self.scroll_fragment.items():
            logger.info(f'👕 {value} × «{scroll_name(scroll_id)}» scroll fragment.')


class Quest(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.state: int = int(raw['state'])
        self.progress: int = int(raw['progress'])
        self.reward: Reward = Reward(raw['reward'])

    @property
    def is_reward_available(self) -> bool:
        return self.state == 2


Quests = List[Quest]


class Letter:
    def __init__(self, item: Dict):
        self.id: str = str(item['id'])


class Hero(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.level: int = int(raw['level'])
        self.color: int = int(raw['color'])
        self.star: int = int(raw['star'])
        self.power: Optional[int] = int(raw.get('power', 0))

        # Should be here to optimise CPU usage.
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
        self.features: Optional[numpy.ndarray] = None

    def set_model(self, model: 'bestmobabot.model.Model'):
        """
        Initialize hero features.
        """
        assert self.features is None, 'model should be set only once for each hero'
        self.features = numpy.fromiter((self.feature_dict.get(name, 0.0) for name in model.feature_names), numpy.float)

    def dump(self) -> dict:
        return {key: self.raw[key] for key in ('id', 'level', 'color', 'star')}

    def order(self):
        """
        Get comparison order.
        """
        return self.star, self.color, self.level

    def __str__(self):
        return f'{"⭐" * self.star} {hero_name(self.id)} ({self.level}) {constants.COLORS.get(self.color, self.color)}'


class BaseArenaEnemy(BaseResponse, metaclass=ABCMeta):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.user_id: str = str(raw['userId'])
        self.place: str = str(raw['place'])
        self.power: int = int(raw['power'])
        self.user: Optional[User] = User(raw['user']) if raw.get('user') else None


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
        self.arena_place: Optional[str] = raw['state'].get('arenaPlace')
        self.grand_place: Optional[str] = raw['state'].get('grandPlace')
        self.battles: List['BattleResult'] = [BattleResult(result) for result in raw['battles']]
        self.reward: Reward = Reward(raw['reward'] or {})


class BattleResult(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.win: bool = raw['result']['win']
        self.stars: int = int(raw['result'].get('stars', 0))


class Boss(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])


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
        self.defenders: List[List[Hero]] = [[Hero(hero) for hero in defenders.values()] for defenders in raw['defenders']]


class ShopSlot(BaseResponse):
    def __init__(self, raw: Dict):
        super().__init__(raw)
        self.id: str = str(raw['id'])
        self.is_bought: bool = bool(raw['bought'])
        self.reward: Reward = Reward(raw['reward'])


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


__all__ = [
    'BaseResponse',
    'Result',
    'User',
    'Expedition',
    'Reward',
    'Quest',
    'Quests',
    'Letter',
    'Hero',
    'BaseArenaEnemy',
    'ArenaEnemy',
    'GrandArenaEnemy',
    'ArenaResult',
    'BattleResult',
    'Boss',
    'Battle',
    'Replay',
    'ShopSlot',
    'Tower',
]
